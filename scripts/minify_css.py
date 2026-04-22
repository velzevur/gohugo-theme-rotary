#!/usr/bin/env python3
from pathlib import Path
import sys


def strip_comments(css):
    out = []
    i = 0
    quote = None
    while i < len(css):
        char = css[i]
        nxt = css[i + 1] if i + 1 < len(css) else ""
        if quote:
            out.append(char)
            if char == "\\" and i + 1 < len(css):
                i += 1
                out.append(css[i])
            elif char == quote:
                quote = None
        elif char in ("'", '"'):
            quote = char
            out.append(char)
        elif char == "/" and nxt == "*":
            i += 2
            while i + 1 < len(css) and not (css[i] == "*" and css[i + 1] == "/"):
                i += 1
            i += 1
        else:
            out.append(char)
        i += 1
    return "".join(out)


def minify(css):
    css = strip_comments(css)
    out = []
    quote = None
    pending_space = False
    for char in css:
        if quote:
            out.append(char)
            if char == quote:
                quote = None
            continue

        if char in ("'", '"'):
            if pending_space and out and out[-1] not in "{}:;,>+~([":
                out.append(" ")
            pending_space = False
            quote = char
            out.append(char)
            continue

        if char.isspace():
            pending_space = True
            continue

        if char in "{}:;,>+~":
            while out and out[-1] == " ":
                out.pop()
            out.append(char)
            pending_space = False
            continue

        if pending_space and out and out[-1] not in "{}:;,>+~([":
            out.append(" ")
        pending_space = False
        out.append(char)

    return "".join(out).strip()


def main():
    if len(sys.argv) < 2:
        print("usage: minify_css.py <css-file> [<css-file> ...]", file=sys.stderr)
        return 2

    for name in sys.argv[1:]:
        path = Path(name)
        original = path.read_text()
        compressed = minify(original) + "\n"
        path.write_text(compressed)
        print(f"{path}: {len(original)} -> {len(compressed)} bytes")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
