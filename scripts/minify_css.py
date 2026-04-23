#!/usr/bin/env python3
import argparse
import fnmatch
import re
from pathlib import Path


KEEP_SELECTOR_PATTERNS = (
    "html",
    "body",
    "main",
    "section",
    "article",
    "aside",
    "header",
    "footer",
    "nav",
    "a",
    "p",
    "ul",
    "ol",
    "li",
    "img",
    "figure",
    "figcaption",
    "picture",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "blockquote",
    "code",
    "pre",
    "input",
    "textarea",
    "select",
    "button",
    "svg",
    "path",
    "span",
    "div",
    ".is-active",
    ".is-clipped",
    ".pswp*",
    ".fa*",
    ".svg-inline--fa",
)

CONTENT_EXTENSIONS = {
    ".html",
    ".htm",
    ".md",
    ".markdown",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".js",
    ".ts",
}

CLASS_OR_ID_RE = re.compile(r"[#.]-?[_a-zA-Z]+[_a-zA-Z0-9-]*")


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


def read_content_tokens(paths):
    tokens = set()
    for root in paths:
        root = Path(root)
        if not root.exists():
            continue
        files = [root] if root.is_file() else root.rglob("*")
        for path in files:
            if not path.is_file() or path.suffix.lower() not in CONTENT_EXTENSIONS:
                continue
            if any(part in {"node_modules", "resources", ".git"} for part in path.parts):
                continue
            try:
                text = path.read_text(errors="ignore")
            except OSError:
                continue
            tokens.update(re.findall(r"[_a-zA-Z][-_a-zA-Z0-9]*", text))
    return tokens


def split_selector_list(selector_text):
    selectors = []
    start = 0
    depth = 0
    quote = None
    for i, char in enumerate(selector_text):
        if quote:
            if char == "\\":
                continue
            if char == quote:
                quote = None
        elif char in ("'", '"'):
            quote = char
        elif char in "([":
            depth += 1
        elif char in ")]" and depth:
            depth -= 1
        elif char == "," and depth == 0:
            selectors.append(selector_text[start:i].strip())
            start = i + 1
    selectors.append(selector_text[start:].strip())
    return [selector for selector in selectors if selector]


def selector_is_kept(selector, used_tokens):
    compact = re.sub(r":{1,2}[-_a-zA-Z0-9()\"'= ]+", "", selector)
    selector_tokens = CLASS_OR_ID_RE.findall(compact)
    if not selector_tokens:
        first = re.match(r"^\s*([_a-zA-Z][-_a-zA-Z0-9]*)", compact)
        return not first or first.group(1) in used_tokens or selector_matches_keeplist(first.group(1))

    for token in selector_tokens:
        name = token[1:]
        if name in used_tokens or selector_matches_keeplist(token):
            return True
    return False


def selector_matches_keeplist(selector):
    selector = selector.strip()
    bare = selector.lstrip(".#")
    return any(
        fnmatch.fnmatch(selector, pattern) or fnmatch.fnmatch(bare, pattern)
        for pattern in KEEP_SELECTOR_PATTERNS
    )


def find_matching_brace(css, open_index):
    depth = 0
    quote = None
    i = open_index
    while i < len(css):
        char = css[i]
        if quote:
            if char == "\\":
                i += 1
            elif char == quote:
                quote = None
        elif char in ("'", '"'):
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def purge_block(css, used_tokens):
    output = []
    position = 0
    while position < len(css):
        open_index = css.find("{", position)
        if open_index == -1:
            output.append(css[position:])
            break

        prelude = css[position:open_index].strip()
        close_index = find_matching_brace(css, open_index)
        if close_index == -1:
            output.append(css[position:])
            break

        output.append(css[position:open_index - len(css[position:open_index].lstrip())])
        body = css[open_index + 1:close_index]
        lower_prelude = prelude.lower()

        if prelude.startswith("@"):
            if lower_prelude.startswith(("@media", "@supports", "@container", "@layer")):
                purged_body = purge_block(body, used_tokens).strip()
                if purged_body:
                    output.append(f"{prelude}{{{purged_body}}}")
            else:
                output.append(f"{prelude}{{{body}}}")
        else:
            kept_selectors = [
                selector for selector in split_selector_list(prelude)
                if selector_is_kept(selector, used_tokens)
            ]
            if kept_selectors:
                output.append(f"{','.join(kept_selectors)}{{{body}}}")

        position = close_index + 1
    return "".join(output)


def purge(css, used_tokens):
    return purge_block(strip_comments(css), used_tokens)


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
    parser = argparse.ArgumentParser(description="Purge unused selectors and minify CSS files.")
    parser.add_argument("--content", action="append", default=[], help="file or directory to scan for used selectors")
    parser.add_argument("css_files", nargs="+", help="CSS file(s) to process in place")
    args = parser.parse_args()

    used_tokens = read_content_tokens(args.content)

    for name in args.css_files:
        path = Path(name)
        original = path.read_text()
        css = purge(original, used_tokens) if used_tokens else original
        compressed = minify(css) + "\n"
        path.write_text(compressed)
        mode = "purged + minified" if used_tokens else "minified"
        print(f"{path}: {len(original)} -> {len(compressed)} bytes ({mode})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
