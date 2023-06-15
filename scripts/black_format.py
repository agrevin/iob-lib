#!/usr/bin/env python3

import argparse
import subprocess


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="black_format",
        description="""Python Black format script.
        Format all python files (*.py) in repository.""",
    )
    parser.add_argument(
        "-c", "--check", action="store_true", help="Check if files need formatting"
    )
    parser.add_argument(
        "-d", "--diff", action="store_true", help="Display format changes"
    )

    args = parser.parse_args()

    black_flags = ""
    if args.check:
        black_flags += " --check"
    if args.diff:
        black_flags += " --diff"

    # git ls-files: pipe only git tracked files into black. Does not include
    # submodule files
    files = subprocess.run(
        f"git ls-files *.py",
        shell=True,
        check=True,
        capture_output=True,
        text=True,
    )

    # format each file
    for fname in files.stdout.split("\n"):
        if fname.strip():
            format_cmd = f"black {fname}"
            subprocess.run(format_cmd, shell=True, check=True)
            print(format_cmd)
