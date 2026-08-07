#!/usr/bin/env python3
"""ob1-review picker — mouse-driven triage of the Open Brain action queue.

Reads a proposal file, lets Simon flip the ones the agent got wrong, writes the
confirmed dispositions back out. Stdlib only; talks to /dev/tty directly so it
works regardless of how stdin/stdout are wired.

    picker.py --items items.json --out out.json
    picker.py --items items.json --selftest    # render one frame, no raw mode

items.json  {"title": str, "items": [{"memory_id": int, "item_index": int,
                                      "text": str, "context": str,
                                      "proposal": "promote"|"clear"|"defer",
                                      "note": str}]}
out.json    {"status": "applied"|"cancelled",
             "items": [{"memory_id": int, "item_index": int,
                        "disposition": str, "text": str}]}
"""

import argparse
import json
import os
import signal
import sys
import termios
import textwrap
import tty

BADGE = {
    "promote": ("PROMOTE", "\x1b[1;32m"),
    "defer":   ("DEFER  ", "\x1b[1;33m"),
    "clear":   ("CLEAR  ", "\x1b[2;37m"),
    "rule":    ("RULE   ", "\x1b[35m"),
    "explain": ("EXPLAIN", "\x1b[1;36m"),
}
CYCLE = list(BADGE)  # one order everywhere: click, ← and → all walk all five
KEYS = {"p": "promote", "d": "defer", "c": "clear", "r": "rule", "e": "explain"}
RESET, DIM, BOLD, INV = "\x1b[0m", "\x1b[2m", "\x1b[1m", "\x1b[7m"
GUTTER = 11  # 2 cursor + 7 badge + 2 gap


class Picker:
    def __init__(self, title, items, tty_in, tty_out):
        self.title = title
        self.items = items
        self.tin, self.tout = tty_in, tty_out
        self.cursor = 0
        self.top = 0
        self.dirty = True
        self.resize()

    def resize(self, *_):
        try:
            size = os.get_terminal_size(self.tout.fileno())
            self.w, self.h = size.columns, size.lines
        except OSError:
            self.w, self.h = 80, 24
        self.w = max(self.w, 40)
        self.h = max(self.h, 12)
        self.dirty = True

    # ---------- layout ----------

    def build_lines(self):
        """Flatten items into screen lines, remembering which item each belongs to."""
        lines = []
        width = self.w - GUTTER - 1
        section = None
        for idx, it in enumerate(self.items):
            # Section headers exist so auto-resolved rows are always on screen
            # rather than resolved behind Simon's back. They are not selectable.
            if it.get("section") and it["section"] != section:
                section = it["section"]
                bar = f"── {section} "
                lines.append((f"{DIM}{bar}{'─' * max(0, self.w - len(bar) - 3)}{RESET}", None, False))
            label, colour = BADGE[it["disposition"]]
            # The id has to be inside the wrap, not prepended after it — otherwise
            # the head line runs past the terminal width, wraps, and pushes the
            # whole frame up by a row.
            tag = f"#{it['memory_id']}[{it['item_index']}]"
            body = textwrap.wrap(f"{tag} {it['text']}", width) or [""]
            first = body[0].replace(tag, f"{BOLD}{tag}{RESET}", 1)
            lines.append((f"{colour}{label}{RESET}  {first}", idx, True))
            for cont in body[1:]:
                lines.append((" " * (GUTTER - 2) + cont, idx, False))
            if it.get("note"):
                for cont in textwrap.wrap(f"↳ {it['note']}", width):
                    lines.append((f"{DIM}{' ' * (GUTTER - 2)}{cont}{RESET}", idx, False))
        return lines

    def counts(self):
        out = {k: 0 for k in BADGE}
        for it in self.items:
            out[it["disposition"]] += 1
        return out

    def render(self):
        lines = self.build_lines()
        ctx_h = 4
        body_h = self.h - 2 - ctx_h  # header + footer + context pane
        body_h = max(body_h, 3)

        # keep the cursor's first line in view
        first = next((i for i, (_, idx, head) in enumerate(lines)
                      if idx == self.cursor and head), 0)
        last = max((i for i, (_, idx, _) in enumerate(lines) if idx == self.cursor),
                   default=first)
        if first < self.top:
            self.top = first
        if last >= self.top + body_h:
            self.top = last - body_h + 1
        self.top = max(0, min(self.top, max(0, len(lines) - body_h)))

        c = self.counts()
        plain = "  ".join(f"{c[k]} {k}" for k in BADGE if c[k])
        tally = "  ".join(f"{BADGE[k][1]}{c[k]} {k}{RESET}" for k in BADGE if c[k])
        title = self.title[:max(0, self.w - len(plain) - 6)]
        out = ["\x1b[H"]
        out.append(f" {BOLD}{title}{RESET}   {tally}\x1b[K\r\n")

        view = lines[self.top:self.top + body_h]
        self.line_map = []
        for text, idx, is_head in view:
            mark = "▸ " if (idx == self.cursor and is_head) else "  "
            prefix = INV + mark + RESET if idx == self.cursor and is_head else mark
            out.append(prefix + text + "\x1b[K\r\n")
            self.line_map.append(idx)
        for _ in range(body_h - len(view)):
            out.append("\x1b[K\r\n")
            self.line_map.append(None)

        cur = self.items[self.cursor]
        out.append(f"{DIM}{'─' * (self.w - 1)}{RESET}\x1b[K\r\n")
        ctx = textwrap.wrap(cur.get("context", ""), self.w - 3)[:ctx_h - 1]
        for line in ctx:
            out.append(f"{DIM}  {line}{RESET}\x1b[K\r\n")
        for _ in range(ctx_h - 1 - len(ctx)):
            out.append("\x1b[K\r\n")

        hint = " click / ← → cycle · 2-finger = explain · p d c r e · [a]pply · [q]uit"
        out.append(f"{DIM}{hint[:self.w - 1]}{RESET}\x1b[K\x1b[J")
        self.tout.write("".join(out))
        self.tout.flush()

    # ---------- interaction ----------

    def cycle(self, idx, backwards=False):
        it = self.items[idx]
        step = -1 if backwards else 1
        it["disposition"] = CYCLE[(CYCLE.index(it["disposition"]) + step) % len(CYCLE)]
        self.dirty = True

    def label(self, idx, disposition):
        self.items[idx]["disposition"] = disposition
        self.dirty = True

    def move(self, delta):
        self.cursor = max(0, min(len(self.items) - 1, self.cursor + delta))
        self.dirty = True

    def click(self, row):
        i = row - 2  # 1-based row, minus header
        if 0 <= i < len(self.line_map) and self.line_map[i] is not None:
            idx = self.line_map[i]
            if idx == self.cursor:
                self.cycle(idx)
            else:
                self.cursor = idx
                self.dirty = True

    def read_event(self):
        ch = self.tin.read(1)
        if ch != "\x1b":
            return ("key", ch)
        seq = self.tin.read(1)
        if seq != "[":
            return ("key", "\x1b")
        rest = ""
        while True:
            c = self.tin.read(1)
            rest += c
            if c.isalpha() or c == "~":
                break
            if len(rest) > 32:
                return ("key", "")
        if rest.startswith("<"):  # SGR mouse
            try:
                body, kind = rest[1:-1], rest[-1]
                btn, col, row = (int(p) for p in body.split(";"))
            except ValueError:
                return ("key", "")
            if btn == 64:
                return ("scroll", -3)
            if btn == 65:
                return ("scroll", 3)
            if kind == "M" and btn == 0:
                return ("click", row)
            if kind == "M" and btn == 2:  # right-click flags for explanation
                return ("rclick", row)
            return ("key", "")
        return ("key", {"A": "up", "B": "down", "C": "right", "D": "left"}.get(rest[0], ""))

    def run(self):
        while True:
            if self.dirty:
                self.render()
                self.dirty = False
            kind, val = self.read_event()
            if kind == "click":
                self.click(val)
            elif kind == "rclick":
                i = val - 2
                if 0 <= i < len(self.line_map) and self.line_map[i] is not None:
                    self.cursor = self.line_map[i]
                    self.label(self.cursor, "explain")
            elif kind == "scroll":
                self.move(val)
            elif kind == "key":
                if val in ("q", "\x03", "\x1b"):
                    return "cancelled"
                if val == "a":
                    return "applied"
                if val == "down":
                    self.move(1)
                elif val == "up":
                    self.move(-1)
                elif val in (" ", "\r", "\n", "right"):
                    self.cycle(self.cursor)
                elif val == "left":
                    self.cycle(self.cursor, backwards=True)
                elif val in KEYS:
                    self.label(self.cursor, KEYS[val])
                elif val == "G":
                    self.cursor = len(self.items) - 1
                    self.dirty = True
                elif val == "g":
                    self.cursor = 0
                    self.dirty = True


def load(path):
    with open(path) as fh:
        data = json.load(fh)
    items = data["items"]
    if not items:
        raise SystemExit("picker: nothing to triage")
    for it in items:
        it["disposition"] = it.get("proposal", "clear")
        if it["disposition"] not in BADGE:
            raise SystemExit(f"picker: bad proposal {it['disposition']!r}")
    return data.get("title", "ob1 review"), items


def write_out(path, status, items):
    payload = {"status": status, "items": [
        {"memory_id": it["memory_id"], "item_index": it["item_index"],
         "disposition": it["disposition"], "text": it["text"]} for it in items]}
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True)
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    title, items = load(args.items)

    if args.selftest:
        p = Picker(title, items, sys.stdin, sys.stdout)
        p.w, p.h = 88, 26
        p.render()
        sys.stdout.write("\n")
        return 0

    if not args.out:
        raise SystemExit("picker: --out is required")

    tin = open("/dev/tty", "r", buffering=1)
    tout = open("/dev/tty", "w")
    fd = tin.fileno()
    saved = termios.tcgetattr(fd)
    p = Picker(title, items, tin, tout)
    def bail(signum, frame):
        raise KeyboardInterrupt

    try:
        signal.signal(signal.SIGWINCH, p.resize)
        # Closing the window sends SIGHUP. Without this the process dies before
        # writing anything and the whole batch of decisions is lost.
        signal.signal(signal.SIGHUP, bail)
        signal.signal(signal.SIGTERM, bail)
    except ValueError:
        pass
    status = "interrupted"
    try:
        tty.setraw(fd)
        tout.write("\x1b[?1049h\x1b[?25l\x1b[?1000h\x1b[?1006h")
        tout.flush()
        status = p.run()
    except KeyboardInterrupt:
        pass
    finally:
        # A closing window can deliver a second SIGHUP mid-cleanup; ignore signals
        # from here on and never let a dead tty stop the file from being written.
        for sig in (signal.SIGHUP, signal.SIGTERM, signal.SIGWINCH):
            try:
                signal.signal(sig, signal.SIG_IGN)
            except (ValueError, OSError):
                pass
        write_out(args.out, status, items)
        try:
            tout.write("\x1b[?1006l\x1b[?1000l\x1b[?25h\x1b[?1049l")
            tout.flush()
            termios.tcsetattr(fd, termios.TCSADRAIN, saved)
        except (OSError, termios.error):
            pass

    c = p.counts()
    try:
        print(f"{status}: " + ", ".join(f"{c[k]} {k}" for k in BADGE if c[k]))
    except OSError:
        pass
    return 0 if status == "applied" else 1


if __name__ == "__main__":
    sys.exit(main())
