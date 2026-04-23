#!/usr/bin/env python3
"""Upload only changed Hugo output files with lftp.

The script keeps a local checksum manifest of the last successful deploy.
This avoids re-uploading every file after Hugo rewrites the public directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import subprocess
import sys
import tempfile
from pathlib import Path


DEFAULT_MANIFEST = Path(".deploy/manifest.json")
IGNORED_NAMES = {".DS_Store"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload changed/new files from a built Hugo public directory."
    )
    parser.add_argument("public_dir", help="Built Hugo output directory, usually public")
    parser.add_argument("host", help="FTP host passed to lftp")
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST),
        help=f"Path to the deploy manifest (default: {DEFAULT_MANIFEST})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the files that would be uploaded without calling lftp",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Upload every file and refresh the manifest after a successful upload",
    )
    parser.add_argument(
        "--mark-deployed",
        action="store_true",
        help="Record the current public directory as deployed without uploading",
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(public_dir: Path) -> dict[str, str]:
    manifest: dict[str, str] = {}
    for path in sorted(public_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name in IGNORED_NAMES:
            continue

        rel_path = path.relative_to(public_dir).as_posix()
        if "\n" in rel_path:
            raise ValueError(f"Cannot deploy path containing a newline: {rel_path!r}")
        manifest[rel_path] = sha256_file(path)
    return manifest


def load_manifest(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in data.items()
    ):
        raise ValueError(f"Invalid manifest format: {path}")

    return data


def save_manifest(path: Path, manifest: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")


def lftp_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def lftp_script(host: str, public_dir: Path, files: list[str]) -> str:
    directories = sorted(
        {posixpath.dirname(file_path) for file_path in files if posixpath.dirname(file_path)}
    )

    lines = [
        "set ftp:ssl-allow off",
        f"open {lftp_quote(host)}",
        f"lcd {lftp_quote(str(public_dir))}",
    ]

    for directory in directories:
        lines.append(f"mkdir -pf {lftp_quote(directory)}")

    total_files = len(files)
    for index, file_path in enumerate(files, start=1):
        directory = posixpath.dirname(file_path) or "."
        remaining = total_files - index
        percent = round(index * 100 / total_files)
        lines.append(
            "echo "
            + lftp_quote(
                f"[{index}/{total_files}] {percent}% uploaded, {remaining} left: {file_path}"
            )
        )
        lines.append(f"put -O {lftp_quote(directory)} {lftp_quote(file_path)}")

    lines.append("exit")
    return "\n".join(lines) + "\n"


def run_lftp(script: str) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
        handle.write(script)
        script_path = handle.name

    try:
        subprocess.run(["lftp", "-f", script_path], check=True)
    finally:
        os.unlink(script_path)


def main() -> int:
    args = parse_args()
    public_dir = Path(args.public_dir)
    manifest_path = Path(args.manifest)

    if not public_dir.is_dir():
        print(f"Missing public directory: {public_dir}", file=sys.stderr)
        return 1

    current_manifest = build_manifest(public_dir)
    if args.mark_deployed:
        save_manifest(manifest_path, current_manifest)
        print(f"Recorded {len(current_manifest)} file(s) in {manifest_path}.")
        return 0

    previous_manifest = {} if args.force else load_manifest(manifest_path)
    changed_files = [
        file_path
        for file_path, digest in current_manifest.items()
        if previous_manifest.get(file_path) != digest
    ]

    if not changed_files:
        print("No changed or new files to upload.")
        return 0

    print(f"Uploading {len(changed_files)} changed/new file(s).")
    if args.dry_run:
        for file_path in changed_files:
            print(file_path)
        return 0

    run_lftp(lftp_script(args.host, public_dir, changed_files))
    save_manifest(manifest_path, current_manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
