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

Banking tests model the separate code/data selectors and the firmware's
callable-page entry/return contract. They verify restoration of the caller's
data selector, calls from different code banks, preservation of DEF USR
pointers and unrelated banks, and no access to reserved hardware addresses.
The paging logic is modeled, not a test of the actual Pico firmware.

The original features were tested successfully by Rusty on a 48K Model I K
with the author's Floppy80, both on Beta1 and on upstream 655970e. This revision
incorporates upstream c26463b and migrates history to the independent data-bank
window. That data-bank revision passed hardware testing; the configurable-history retry still needs its own physical hardware check.

Configurable-history tests exercise all capacities 1-20, rollover, draft
restoration, maximum-length commands, malformed/missing configuration,
UTF-8 BOM, 256-byte block boundaries, and one-time initialization on DOS input.
Persistent BUSY and oversized input cases verify bounded return to the prompt.
An integration test executes the actual BOOT.SYS machine code and streams
SYSP.sys through mocked SD ports, checking the resulting banks and transfer
to STARTUP. It does not emulate BASIC ROM initialization or real board timing.
