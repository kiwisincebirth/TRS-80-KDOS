
## Version - Beta 2

#### Unreleased

New Features
* [RS] DOS Command line Input History, with up to 20 items
* [RS] Basic CMD "COMMAND" to execute DOS internal commands
* [RS] Sequential BASIC OPEN, CLOSE, PRINT#, INPUT#, LINE INPUT# and EOF, with up to 16 files
* [RS] DOS file-byte I/O through ROM GET/PUT for open FCBs with one-byte records (paged DOS)
* [RS] IOCHECK.BAS and SIMPLEIO.BAS hardware tests under SYS/test in the SD-card build
* [MP] COPY Command with support for wildcards, requires Beta4 firmware
* [MP] Basic KILL "FILE/EXT" Command
* [MP] @DATE and @TIME DOS API support

Improvements
* [RS] DIR command supports BREAK to abort
* [MP] DEL Command updated to support wildcards, requires Beta4 firmware
* [MP] HELP command, added some missing commands
* [MP] HELP command, non-paged version now excludes unsupported commands
* [MP] Error message, when removing a directory that isnt empty
* [MP] Error Message, when creating directory that already exists
* [MP] Technical Loader code in Extra Ram move it to $4000

Bug Fixes
* [MP] Bug with DOS LOAD command failure in emulation

## Version - Beta 1

#### June 2026

Original Version
