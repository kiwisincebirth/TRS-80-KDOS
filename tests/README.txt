Console regression tests execute compiled Z80 code using Ivan Kosarev's
MIT-licensed z80 emulator, version 1.2.0. ROM console routines and Floppy80
ports are mocked; these are not a complete hardware emulation.

Install dependencies with Python 3.10 or later:
  python -m pip install -r tests/requirements.txt

After building, run:
  python tests/test_console.py

For another build location, add --build-dir PATH. Expected layout:
  PATH/SD-CARD/SYS/SYSP.sys
  PATH/SD-CARD/SYS/overlayd.sys
  PATH/src/zout/SYS0P.lst

Tests cover eight-entry history rollover, both navigation boundaries, draft
restoration, cancellation, editing, the 127-character limit, bank restoration,
and actual DOS shell dispatch. Directory cases cover first/later page BREAK,
normal continuation, hidden entries, empty/short/exact-page directories,
FreHD early exit, Pico stream consumption, and absence of screen-clear codes.

The equivalent changes on Beta1 were tested successfully by Rusty on a 48K
Model I K with the author's Floppy80. This branch applies them to current
upstream; that combined version still needs a physical hardware check.
