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

Sequential BASIC file I/O tests
After building and installing the same Python dependency, supply your own
12 KiB Model I Level II-compatible ROM. No ROM is distributed with this project.
The development tests used the System 80 original ROM from the author's
TRS-80-ROMS repository; other ROM variants have not been validated.

PowerShell:
  $env:KDOS_TEST_ROM = 'C:\path\to\system80_original.rom'
  python tests/test_basic_io.py

These tests execute the real ROM tokenizer, interpreter, expression evaluator,
variables, arrays and string garbage collector, together with the compiled
kDOS handlers. They cover sixteen simultaneous files, repeated EOF lookahead,
numeric/string fields, double precision, CR/LF variants, length boundaries,
file errors, nested EOF expressions, and automatic close on END.
The test harness intercepts errors at the ROM error entry; it does not prove
full error recovery. Pico ports and banking are modeled, so hardware timing,
firmware compatibility and actual SD-card persistence still require testing.

The suite executes tests/IOCHECK.txt and tests/SIMPLEIO.txt, checks their
step-by-step results, and verifies they match the tokenized files in
SYS/Tests and the build/SD-CARD/SYS/tests staging directory. The checked-in
.BAS files are copied by normal builds; no ROM or Python is needed to stage
these programs. The .txt files are readable listings, not LOADable files.
When changing a listing, regenerate its tokenized .BAS using a compatible
BASIC tokenizer and run this suite to verify that both versions match.

BASIC CMD tests
Use the same Python dependency, and supply your own 12 KiB Model I Level II-
compatible ROM. Development tests used system80_original.rom from the
author's TRS-80-ROMS repository. No ROM is included with this contribution.

PowerShell, after building:
  $env:KDOS_TEST_ROM = 'C:\path\to\system80_original.rom'
  python tests/test_basic_commands.py

Tests execute the real ROM tokenizer, expressions, interpreter and error
handler, plus the compiled DOS command parser/directory/delete services.
They cover direct mode, colon continuation, loops/GOSUB, nested expressions,
directory paging/BREAK, invalid commands, delete errors, state cleanup, and
existing BASIC LOAD/RUN. Direct @CMNDI tests cover success/error status,
CR/NUL input, nested-call rejection, stack balance and caller-bank restoration.
CMD LOAD tests execute the real record loader for ordinary RAM and a separate
code bank, check continuation without execution, and verify loader errors.
Pico ports/filesystem and paging are simulated;
the tests do not replace physical Floppy80 verification.

The suite generates build/SD-CARD/CMDCHECK.BAS (tokenized, LOADable) and
build/SD-CARD/CMDTEST.TMP (disposable deletion target). tests/CMDCHECK.txt is
the human-readable program listing. A normal build alone does not generate
these test artifacts. Recreate/copy CMDTEST.TMP before repeating the test.

Combined-feature regression: python tests/test_basic_combined.py
Keeps a sequential file open across CMD, continues writing, reads it back,
and uses CMD DEL after closing it. Uses the same ROM and emulator dependency.

PR #27 regression coverage also calls ROM _GET/$0013 and _PUT/$001B with
an FCB in ordinary RAM, checks caller registers/banks, raw CR/LF and EOF,
and verifies that @INIT retains contents while BASIC OPEN O truncates.
The shared DOS byte driver currently requires a file opened with LRL=1;
other record sizes return Illegal DOS function until buffering is added.
