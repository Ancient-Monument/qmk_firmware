# Ancient-Monument/qmk_firmware

A fork of [qmk/qmk_firmware](https://github.com/qmk/qmk_firmware) that exists to hold
Ross's handwired boards under `keyboards/handwired/`: `am37`, `am49`, `am96`, `zf65`,
`vc3`, plus the fork's own tooling in `tools/rharmes/`. Nothing else in the tree is ours.
It moved from the `rharmes` account to the Ancient-Monument org on 2026-09-29 (#14);
GitHub redirects the old URLs, and `tools/rharmes/` keeps its name.
`~/.claude/CLAUDE.md` holds the working defaults; this file holds the exceptions and the
build workflow.

## Branches

- **`master` is upstream `master` plus our files** (the boards, `tools/rharmes/`, this
  file), merged in by PR. Pull upstream in on GitHub with
  `gh repo sync Ancient-Monument/qmk_firmware --source qmk/qmk_firmware --branch master`
  (needs the `workflow` token scope). It merges upstream into `master` as a merge commit
  (first run 2026-09-29, #14). **Never pass `--force`**: it hard-resets `master` to
  upstream and drops our files. Afterwards `git fetch origin`, fast-forward, and build all
  five boards to catch upstream breakage. Never commit to `master` directly.
  Two upstream workflows are disabled in this repo's Actions settings on GitHub, which is
  invisible in the tree: `Regenerate Files` (`regen_push.yml`, #10) and `CI Build Major
  Branch` (`ci_build_major_branch.yml`, #11). Both run on every push to `master`, and both
  guard their real work (opening a regen PR, building every keyboard) with
  `if: github.repository == 'qmk/qmk_firmware'`, so here regen discards its output and the
  build is skipped. Disabled, they cost no Actions minutes and stay inert if upstream ever
  drops those guards.
- **Run `gh` with the default repo set.** `gh` ranks an `upstream` remote above `origin`,
  so with no default a bare `gh issue view` or `gh pr create` here targets
  `qmk/qmk_firmware`. `gh repo set-default Ancient-Monument/qmk_firmware` pins it for this
  checkout (set 2026-09-29); pass `--repo` if a command still resolves upstream.
- **Work on a branch off `master`** and land it with a PR. The boards, `tools/rharmes/`
  and this file are the only files any branch should touch.
- **`dev` is frozen.** It is the QMK 0.9.46-era tree the boards ran on until September
  2026, tagged `legacy-0.9.46`. See *Legacy firmware* below.
- **Tasks live in this repo's GitHub Issues**, referenced as `#n`.

## Building and flashing

Toolchain is upstream's macOS setup: `brew install qmk/qmk/qmk` plus force-linked
`avr-gcc@8`, `arm-none-eabi-gcc@8` and `arm-none-eabi-binutils`. `qmk doctor` must be
clean before blaming a board. The `qmk` CLI only works inside a modern checkout; run in the
legacy tree it dies with `conflicting subparser: config`.

    qmk compile -kb handwired/am37 -km default
    qmk flash   -kb handwired/am37 -km default    # waits for the bootloader

All boards are `atmega32u4`. `am37`, `am49`, `am96` and `zf65` use `qmk-dfu`; `vc3` uses
`caterina`. Flashing a `qmk-dfu` board by hand needs `dfu-programmer atmega32u4 erase
--force` first, or `flash` fails with `Memory write error`.

clangd: run `tools/rharmes/compiledb.py` (about three minutes) to build
`compile_commands.json` for all five boards, then restart the session so clangd drops its
guessed flags. It wraps `qmk compile --compiledb`, which handles one board, cleans `.build`
and never lists `keymap.c` (modern QMK compiles it by `#include`), and fixes each of those.
Rerun it after touching `keyboard.json` or a `rules.mk`, since features become `-D` flags,
and after any clean build: `make clean`, `qmk compile --clean` or a single-board
`qmk compile --compiledb` all delete the generated headers the database points at, and
clangd then reports dozens of phantom errors. Every shared source (everything except the
five keymaps and each board's generated `default_keyboard.c`) is analysed with the flags
of the first board in the script's `BOARDS` list, currently `am37`.
`compile_commands.json` stays in `.git/info/exclude`; `.clangd` is upstream's, tracked.

## Legacy firmware

The tag `legacy-0.9.46` (commit `b8adf11a45`) is the last pre-port tree and still builds
with the same `avr-gcc@8`:

    git checkout legacy-0.9.46
    export PATH="/opt/homebrew/opt/avr-gcc@8/bin:$PATH"
    make handwired/<board>:default

The `.hex` files built from that tag on 2026-09-20 are kept outside the repo in
`~/Developer/qmk-legacy-firmware/`, with flashing notes in its README.
