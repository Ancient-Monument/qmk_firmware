#!/usr/bin/env python3
"""Build a clangd compile_commands.json covering all of Ross's handwired boards.

`qmk compile --compiledb` writes a database for one keyboard, cleans `.build`
first, and never lists keymap.c (modern QMK compiles it by #include from
quantum/keymap_introspection.c). clangd then guesses flags for keymap.c from
whichever file is nearest, which is the wrong board for all but one keymap.

This script runs the generator per board, checks the database it wrote really
is that board's (a parse failure inside `--compiledb` leaves the previous file
in place and still exits 0), clones each board's keymap_introspection.c record
for its keymap.c, merges the databases (first board wins, so every shared
source, meaning everything except the six keymaps, each board's generated
default_keyboard.c and the RP2040 sources only am34 compiles, is analysed with BOARDS[0]'s flags), then rebuilds every board but the last so the generated
`.build/obj_*/src/default_keyboard.h` headers the database points at exist.
Each `--compiledb` run's own build is discarded by the next run's clean, so
eleven compiles happen where six would do; that is the price of driving the
stable `qmk` CLI instead of importing its internals.

If generating the database fails or is interrupted, the previous
compile_commands.json is restored. A failure while rebuilding headers leaves
the new database in place and names the board to rebuild.

Usage: tools/rharmes/compiledb.py   (works from any directory; takes ~3 minutes)
"""
import copy
import json
import subprocess
import sys
from pathlib import Path

BOARDS = ["am37", "am49", "am96", "zf65", "vc3", "am34"]
ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "compile_commands.json"
INTROSPECTION = "quantum/keymap_introspection.c"


def qmk_compile(board: str, *extra: str) -> None:
    subprocess.run(["qmk", "compile", "-kb", f"handwired/{board}", "-km", "default", *extra], cwd=ROOT, check=True)


def board_records(board: str) -> list[dict]:
    """Generate the database for one board and return its records, verified."""
    DB.unlink(missing_ok=True)
    qmk_compile(board, "--compiledb")
    if not DB.exists():
        sys.exit(f"{board}: qmk compile --compiledb wrote no {DB.name}")
    records = json.loads(DB.read_text())
    intro = next((r for r in records if r["file"] == INTROSPECTION), None)
    if intro is None or f'-DQMK_KEYBOARD="handwired/{board}"' not in intro["arguments"]:
        sys.exit(f"{board}: {DB.name} has no {INTROSPECTION} record for this board")
    keymap = copy.deepcopy(intro)
    keymap["file"] = f"keyboards/handwired/{board}/keymaps/default/keymap.c"
    return [keymap, *records]


def write_database() -> None:
    seen, merged = set(), []
    for board in BOARDS:
        for record in board_records(board):
            if record["file"] not in seen:
                seen.add(record["file"])
                merged.append(record)
    DB.write_text(json.dumps(merged, indent=4))
    print(f"wrote {DB} with {len(merged)} entries for {', '.join(BOARDS)}")


def rebuild_headers() -> None:
    # --compiledb cleans .build, so only the last board's generated headers survive.
    for board in BOARDS[:-1]:
        try:
            qmk_compile(board)
        except (Exception, KeyboardInterrupt) as err:
            remaining = ", ".join(BOARDS[BOARDS.index(board):-1])
            sys.exit(f"{DB.name} is complete, but .build is missing the {board} headers ({type(err).__name__}); "
                     f"run `qmk compile -kb handwired/<board> -km default` for: {remaining}.")


def main() -> None:
    previous = DB.read_text() if DB.exists() else None
    try:
        write_database()
    except BaseException as err:
        if previous is not None:
            DB.write_text(previous)
            restored = f"the previous {DB.name} was restored"
        else:
            DB.unlink(missing_ok=True)
            restored = f"no {DB.name} was left behind"
        if isinstance(err, subprocess.CalledProcessError):
            detail = f"`{' '.join(err.cmd)}` exited {err.returncode}"
        elif isinstance(err, SystemExit):
            detail = str(err)
        else:
            detail = f"{type(err).__name__}: {err}" if str(err) else type(err).__name__
        sys.exit(f"compiledb failed: {detail}; {restored}. Generated headers in .build are incomplete: rerun this script.")
    rebuild_headers()


if __name__ == "__main__":
    main()
