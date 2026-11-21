# User Guide

## Introduction

kDOS is an operating environment that runs on the Tandy TRS-80 Model 1
providing a TRS-DOS (DOS) like features to Level 2 BASIC

### Requirements

To use this project you will require
* A Tandy TRS-80 Model 1
* A Floppy 80 (M1) with SD card
* An Expansion Interface is not required

## Installation

Format the SD card using FAT32

Copy the files provided to the SD card, ensuring that the /SYS folder is created

If necessary change EnableHighRAM in `HARDWARE.cfg` if running on 16KB machine.

Copy any other files you like utilising any directory structure you like.
Ensure you name files accounting to 8.3 file naming. Longer file names are
truncated to 8.3 but this is not recommended

Install the RP2350 firmware (from /FIRMWARE) onto the (RP2350) Floppy-80 M1

## Startup

Once started you should see the message "kDOS Loaded", and be dropped into a BASIC
"READY>" Prompt. On a modern Enhanced L2 ROM

```
Enhanced Level II BASIC
Release 1.4
47,806 Free Bytes
kDOS Loaded
READY
>_
```

or, on a traditional L2 ROM

```
MEM SIZE?
KDOS LOADED
READY
>_
```

At startup holding the `CLEAR` key will :
* Disable Virtual RAM and instead use Liner Overlay RAM.
* Reduce available ram by 512 bytes needed for overlay loading
* Disable Extended basic features, which require virtual memory.
* Disable any AUTO processing

The `BREAK` key will disable loading entirely, like a Floppy disk
boot disable in a traditional setup.

## General Operation

The system will startup as a normal Level 2 basic system. You can type in a basic program
as you would normally on a non-disk system.

```shell
READY
>_
```

Pressing `ENTER` (without typing a command) will switch between DOS and BASIC prompts.
The `:` prompt is the equivalent of the DOS prompt, where disk commands are entered.

```shell
:_
```

To get a summary of DOS commands type the command "HELP"

```
:HELP
kDOS - (ver Beta.2)
  Press <Enter> to switch from BASIC to DOS : prompt
  Programs can be run by typing name of CMD file
DOS Commands
  DIR <filter> - show dir files  LOAD <file.cmd> - load binary
  CD <path> - change directory   MD <path> - make directory
  COPY <file1> <file2> - single  REN <file1> <file2> - rename
  DEL <file> - delete a file     PWD - show current path
  DI EI - disable/enable Clock
BASIC Commands
  LOAD - SAVE - RUN - KILL - MERGE "<file.bas>"
  &Hxx &Oxxx CVI$ DEF FN USR INSTR$ MKI MID$ TIME$ LINE INPUT
:_    
```

## DOS Input

### Input History

In normal paged-memory mode, the DOS `:` prompt remembers the last eight
submitted commands by default (configurable from 1 to 20). 

| Key                | Action                                                                                          |
|--------------------|-------------------------------------------------------------------------------------------------|
| **Up**             | Recalls older commands                                                                          |
| **Down**           | Recalls newer commnads. Down past the newest restores the draft entered before browsing history. |
| **ENTER**          | To execute. Empty Lines return to Basic.                                                        |
| **Left/Backspace** | Delete from the end, type corrections                                                           |
| **CLEAR**          | Erases the current input                                                                        |
| **BREAK**          | Cancels current input. Cancelled commands are not saved.                                      |

History accepts up to 127 characters per command and lasts until kDOS is
reloaded. It uses code pages 183-184 and data pages 33-39 without reserving additional BASIC RAM.
Holding CLEAR at startup disables history along with the other paged features;
DIR cancellation still works. BASIC input and mid-line editing are unchanged.

### History Capacity

Add or edit `HistorySize=8` in `/SYS/settings.cfg` on the SD card. Valid values
are 1-20. Missing or invalid settings use 8; larger values are capped at 20.
kDOS reads this setting once, when you first enter the DOS prompt after boot.
Reboot to apply a later change. Normal BASIC/kDOS startup does not read it.

Keys are case-insensitive; spaces around `=` and `#`/`;` comments are allowed.
If repeated, the last matching assignment wins. Use a text file smaller than
16 KiB. Read errors, a stuck BUSY response, or an oversized file fall back to
the default. Hardware options remain in `HARDWARE.cfg`; history no longer reads that file.
Remove any old `HistorySize` entry there to avoid confusion.

Edit the repository's `SYS/settings.cfg` to change the build's configuration
copy. Build/Rebuild copies it to `build/SD-CARD/SYS/settings.cfg`.

## DOS Commands

Below is a summary of the suppoerted DOS commands. Noting if running on a FreHD
or under the FreHD TRS80GP emulation only the "FreHD" marked features are supported

| Command            | Description                   | Alias         |
|--------------------|-------------------------------|---------------|
| {filename}         | Runs a CMD program            |               |
| CD {dirName}       | Set working directory         |               |
| COPY {file} {dest} | Copy one or more files        | CP            |
| DELETE {file}, ... | Delete one or more files      | DEL, KILL, RM |
| DIR {wildcard}     | display directory contents    | LS            |
| DI                 | Disable Interrupts / RTC      |               |
| EI                 | Enable Interrupts / RTC       |               |
| HELP               | Display a summary of commands |               |
| LOAD {filename}    | Load a CMD program            |               |
| MKDIR {dirname}    | Make a directory              | MD            |
| PWD                | Display current directory     |               |
| RENAME {f1} {f2}   | rename file or directory      | REN, MOVE, MV |
| RMDIR {directory}  | delete a directory (**TODO**) |               |

### CD Command

Changes the Current Working Directory

#### Syntax

```text
CD {directory}
```
Where:
* {directory} — A directory to change to. When specifying a directory

#### Examples

| Type of Copy                    | Example Command  |     |
|---------------------------------|------------------|-----|
| Change to Root Directory        | CD /             |     |
| Change to Sub Directory of Root | CD /SUBDIR       |     |
| Change to a Sub Directory       | CD SUBDIR        |     |
| Change to a Sub Sub Directory   | CD SUBDIR/SUBSUB |     |
| Change to Parent Directory      | CD ..            |     |
| Change to Relative Directory    | CD ../OTHERDIR   |     |

### COPY Command

Copies a single file or a set of matching files non-interactively (existing
destination files with the same name are overwritten without prompting).

#### Syntax

```text
COPY {sourceFileSpec} {destFileSpec}
```
Where:
* {sourceFileSpec} — A single filename, a path with a filename, or a pattern
  containing * wildcards (case-insensitive).
* {destFileSpec} — A destination filename, a directory path (ending with / or \,
  or naming an existing directory), or a wildcard pattern such as *.BAK.

#### Examples

| Type of Copy               | Example Command              |
|----------------------------|------------------------------|
| Single file copy           | COPY README.TXT README.BAK   |
| Copy into a directory      | COPY DATA.DAT BACKUP/        |
| Copy with a path prefix    | COPY DOCS/NOTES.TXT ARCHIVE/ |
| Wildcard copy to directory | COPY FILE.* BACKUP/          |
|                            | COPY *.TXT BACKUP/           |
| Wildcard copy with mapping | COPY *.DAT *.BAK             |

### DELETE Command

Deletes one or more files non-interactively (aliases: DEL, KILL, RM).
Multiple space-separated filenames or wildcard patterns may be supplied in a
single command. Subdirectories, hidden/system files, macOS ._* files, and
read-only files are skipped.

#### Syntax

```text
DELETE {fileSpec} [,{fileSpec} ...]
```
Where:{fileSpec} — A single filename, a path with a filename, or a pattern
containing * wildcards (case-insensitive).

#### Examples

| Type of Delete        | Example Command         |
|-----------------------|-------------------------|
| Single file delete    | DELETE TEMP.TXT         | 
| Multiple files        | DEL FILE1.BAS FILE2.BAS | 
| Wildcard extension    | DEL *.BAK               | 
| All matching entries  | DEL *                   | 
| Wildcard path delete  | DEL TEMP/*.TMP          | 

#### Output and Errors

* Completed: Displays **N File(s) Deleted.** where N is the total number of
files deleted across all tokens (including 0 if no files matched).
* Partial delete: If an error occurs after one or more files have already
been deleted, displays **N File(s) Deleted, with Error Code.**
* Immediate failure: If no files are deleted and an error occurs (such as
an invalid name or missing target), returns a DOS error status.

### DIR Command

Get a directory listing. Supports Wildcards e.g `DIR *.BAS` Alias supported are `LS`

**tbc**

When viewing the listing
* The listing just shows the names of the files, no file sizes are shown.
* Sub directories are shown with a graphical vertical Bar (|) Prefix
* The directory listing is paged, and will pause after a page, press a key to continue
or press **BREAK** to return to the DOS prompt while
keeping the displayed filenames. 

### MOVE Command

See RENAME command

### RENAME Command

Renames a single file or directory, moves an item to another directory, 
or batch-renames matching files using wildcards (aliases: `REN` `MOVE`, `MV`). 
Wildcard matching applies to files only; subdirectories, hidden/system files, 
are skipped during wildcard renames.

#### Syntax

```text
RENAME {source} {dest}
```

Where:
- {source} — A single file or directory name, a path, or a file wildcard pattern containing * (case-insensitive).
- {dest} — A new name, a target directory path, or a wildcard pattern such as *.OLD or MYWORK.*.

#### Examples

| Type of Rename / Move    | Example Command                 |
|--------------------------|---------------------------------|
| Single file rename       | REN OLDNAME.BAS NEWNAME.BAS     |
| Directory rename         | REN TEMP WORK                   |
| Move file to directory   | MOVE FILE1.BAK TEMP/FILE2.BAK   |
| Wildcard extension swap  | REN *.BAK *.OLD                 |
| Wildcard prefix mapping  | REN MYDB.* MYWORK.*             |

#### Output and Errors

* **Completed:** Displays `N File(s) Renamed.` where `N` is the number of items 
renamed (including `0` if no wildcard entries matched).
* **Partial rename:** If an error occurs after one or more items have already 
been renamed, displays `N File(s) Renamed, with Error <CODE>`.
* **Immediate failure:** If no items are renamed and an error occurs 
(such as an invalid name, missing source, or target conflict), 
returns a DOS error status.

## BASIC Commands

As well as the DOS commands, BASIC itself has been upgraded with
commands to manage disk based files. These are executed from the BASIC prompt

The following are supported

| Command              | Description                     |
|----------------------|---------------------------------|
| LOAD "filename.BAS"  | Load a basic Program            |
| SAVE "filename.BAS"  | Save a program to Disk          |
| RUN "filename.BAS"   | Load and Run a program          |
| KILL "filename.EXT"  | Delete a file                   |
| MERGE "filename.BAS" | Merge a file (todo)             |

Note: Ony Tokenised BAS files are supported. ASCII files will not work.

## BASIC Statements

BASIC itself has been upgraded with
the non-disk I/O statements and extensions. The following are supported

| Command             | Description                     |
|---------------------|---------------------------------|
| &Hxx                | Hexadecimal Constant            |
| &Oxx                | Octo-decimal Constant           |
| CMD "command"       | Execute an internal DOS command |
| CVI CVS CVD         | Convert from String             |
| DEF FNn(A)=A        | Define a User Function          |
| DEF USRn=ADDR       | Define a Call address           |
| FNn(A)              | Invoke a User Function          |
| INSTR(X$,Y$)        | String Search function          |
| LINE INPUT A$       | Input an entire line            |
| MID(X$,N,N)=""      | Mid String Assignment           |
| MKI$ MKS$ MKD$      | Convert to String               |
| TIME$               | RTC Current DateTime            |
| USRn(A)             | Invoke a Call address           |

As well as this BASIC will display the descriptive error messages.

### Sequential File I/O

BASIC programs can read and write ordinary text files on the SD card. Up to sixteen
files may be open at once, numbered **1 through 16**. Filenames use the current
directory unless a path is specified; the maximum filename/path length for
these commands is 31 characters. The existing 8.3 naming guidance applies.

| Syntax                  | Purpose                                                                          |
|-------------------------|----------------------------------------------------------------------------------|
| `OPEN "I",1,"DATA.TXT"` | Open an existing file for sequential input.                                      |
| `OPEN "O",1,"DATA.TXT"` | Create a sequential output file; **replaces its contents if it already exists**. |
| `CLOSE 1`               | Close one file. `CLOSE 1,2` closes a list; `CLOSE` closes all.                   |
| `PRINT#1,A$;",";N`      | Write expressions to a file.                                                     |
| `INPUT#1,A$,N`          | Read text/numeric fields into variables or array elements.                       |
| `LINE INPUT#1,A$`       | Read a complete line into a string, preserving spaces and commas.                |
| `EOF(1)`                | Return 0 when more input remains, or -1 at end of file.                          |

`OPEN` and `CLOSE` also accept a `#` before the file number. Mode letters
may be upper or lower case. `INPUT#` and `LINE INPUT#` must run inside a
BASIC program, following the existing BASIC input-statement restriction.

`PRINT#` uses BASIC's numeric formatting. A semicolon joins items; a comma
advances to the next 16-character print zone. Neither automatically writes
a comma delimiter. To create comma-separated fields, print a literal comma
as shown above. To preserve commas or surrounding spaces inside a string
field, write quotes explicitly, for example:

```basic
PRINT#1,CHR$(34);A$;CHR$(34);",";N
```

A trailing semicolon or comma suppresses the line ending. Otherwise each
`PRINT#` ends with CR/LF. `PRINT#1,` writes a blank line. Strings containing
embedded quotation marks do not have CSV-style escape handling in this version.

`INPUT#` accepts comma-separated fields and line endings; numeric fields may
also be separated by whitespace. Unquoted fields have surrounding spaces
and tabs removed. Quoted fields preserve spaces and commas. `LINE INPUT#`
reads the whole line without its line ending. CR/LF, CR-only and LF-only
files are supported, as is a final line without a line ending. A field or
line may contain at most 255 characters.

`EOF` uses lookahead: calling it repeatedly does not remove input. Check it
before reading; reading beyond the end raises `Input past end`. A file must
be open for input to use `EOF`, `INPUT#`, or `LINE INPUT#`.

Close files when finished. `END`, `NEW`, `CLEAR`, and a fresh `RUN` also close
open files. Explicitly use `CLOSE` before removing the SD card or powering off.

See `tests/IOCHECK.txt` for a complete test program and `BUILDING.txt` for
deployment instructions.

### CMD - Calling DOS commands.

`CMD` accepts a string expression containing an internal DOS
command. It works at the BASIC prompt and inside a program. A successful
command returns to the next BASIC statement; it does not change to the DOS
prompt or discard BASIC variables.

```basic
10 CMD "PWD"
20 CMD "DIR *.BAS"
30 PRINT "BACK IN BASIC"
```

The existing internal commands and aliases are available: `DIR`/`LS`, `CD`,
`PWD`, `COPY`/`CP`, `DEL`/`DELETE`/`KILL`/`RM`, `MD`/`MKDIR`,
`REN`/`RENAME`/`MOVE`/`MV`, `LOAD`, `HELP`, `DI`, and `EI`. A command string may
contain at most 127 characters. For example, `CMD "CD GAMES"` changes the
current directory for later BASIC and DOS file operations.

Directory paging behaves as it does at the DOS prompt. BREAK at a paused
listing stops the listing and resumes BASIC without clearing the screen.
Unknown commands and external program names such as `CMD "GALAXY"` produce
`Illegal function call`. `CMD "LOAD TEST.CMD"` loads binary records without
executing the transfer address, then continues BASIC. The binary must target
memory or banks reserved by your application; loading over BASIC or DOS can
corrupt the running system. Use BASIC's `LOAD` for BASIC programs.

BASIC translates DOS error numbers into BASIC errors. This API does not implement
all historical TRSDOS CMD subcommands.

## Appendix

### Filenames

Files names (including directories) should follow the 8.3 naming convention.
Longer file names will be truncated to 8.3 format. While this is supported
it is not recommended as the '~' character is not consistently displayed
or available on the standard keyboard.

When entering filenames the preference is to use a modern format.
e.g. FILENAME.EXT , but the tradition format of FILENAME/EXT
is generally supported within constrains e.g. PATH/FILENAME/EXT
will be interpreted as PATH/FILENAME.EXT
