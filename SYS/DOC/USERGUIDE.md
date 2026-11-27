# kDOS - User Guide

## Introduction

kDOS is an operating environment that runs on the Tandy TRS-80 Model 1
providing a TRS-DOS (DOS) like features to Level 2 BASIC

The DOS runs alongside Level 2 BASIC, rather than supplanting it.
Typing a DOS command and a BASIC statement are done in the
same shell.

Programs that run on TRS-DOS "should" run under kDOS so long
as they use standard DOS API calls. Programs that directly
access FDC hardware or undocumented (non-standard) API calls will
probably not function, unless patched.

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

Programs (CMD Files) can be executed by typing the name of the program. 

## Concepts

### Filesystem

Files are stored and accessed from SD card in a standard FAT filesystem.
There is no emulation of TRS-80 floppy disk or hard disk drives,
nor any TRS-DOS (like) file-system.

There are no imposed file size limits, or limits on the number of files 
that can be stored. Files copied to the SD card by modern computer, are
directly readable on the TRS-80.

### Filenames

Files names (including directories) should follow the 8.3 naming convention.
Longer file names will be truncated to 8.3 format. While this is supported
it is not recommended as the '~' character is not consistently displayed
or available on the keyboard.

When entering filenames the preference is to use a modern format.
e.g. FILENAME.EXT , but the traditional format of FILENAME/EXT
is generally supported within constrains e.g. PATH/FILENAME/EXT
will be interpreted as PATH/FILENAME.EXT

kDOS has a filename and path sanitiser that supports both modern and
traditional (TRS-DOS) naming conventions. Traditional filenames in the
classic `FILENAME/EXT` syntax are translated modern `FILENAME.EXT` format.

The table below shows some more examples of these conversions, and how
they could be misinterpreted.

| Input Pattern      | Resulting Path    | Resulting Behavior                                 |
|:-------------------|:------------------|:---------------------------------------------------|
| `README.TXT`       | `README.TXT`      | Legal no conversion                                |
| `readme.txt`       | `README.TXT`      | upper case conversion                              |
| `README.TEXT`      | `README`          | TEXT (4 chars) interpreted as password and dropped |
| `README/TXT`       | `README.TXT`      | Treated as Traditional Format and converted        |
| `README/TEXT`      | `README/TEXT`     | TEXT (4 chars) interpreted as part of the path.    |
| `README/TXT.PAS`   | `README/TXT.PAS`  | PAS is treated as a valid extension                |
| `README/TXT.PASS`  | `README.TXT`      | PASS (4 chars) interpreted as password and dropped |
| `README/TEXT.PAS`  | `README/TEXT.PAS` | PAS is treated as a valid extension                |
| `README/TEXT.PASS` | `README/TEXT`     | PASS (4 chars) interpreted as password and dropped |

### Directories

Directories are fully supported, you can nest directories in a hierarchical
structure with and arbitrary depth, limited only by 128 character path length.

For a program perspective you will only have access to files in the current directory,
unless you use a path specification to locate the file.

The following are legal user of directory names

| Input Pattern        | Resulting Behavior                        |
|:---------------------|:------------------------------------------|
| `/BASIC/FILE.BAS`    | Absolute path from the root directory     |
| `SUBDIR/FILE.BAS`    | SubDirectory from the current directory   |
| `./SUBDIR/FILE.BAS`  | SubDirectory from the current directory   |
| `../DIR/FILE.BAS`    | Relative Path from the parent directory   |
| `../../DIR/FILE.BAS` | Relative Path traversing multiple levels  |

Standard commands such as CD, PWD, MKDIR, etc. exist to manipulate directories

#### /SYS Directory

The `/SYS` directory holds the system files, be careful about deleting 
or replacing these as they used to boot the system

#### /USR Directory

The `/USR` directory is used as a secondary search location for opening a 
user program of file. It acts like a PATH in MS-DOS, and files will be
searched for here when cannot be found normally. 

You are free to place any programs of files here that you would commonly 
use, however by convention these should be READ-ONLY

If you specify a path as part of the filename (e.g. `/PENCIL/OVERLAY1.OVL`) 
the file will **NOT** be searched in `/USR` 

### Logical Drives

Use the `:D` suffix (1-9) to quickly access different Logical Drives 
or directories configured on your SD card. e.g.

```text
> LOAD "MYGAME.BAS:9"
```

will load the MYGAME basic file from the 9'th logical drive.

However, specifying a path and a logic drive is illegal
(e.g. `/BASIC/MYGAME.BAS:9`) because there are now 2 mechanisms
being used to specify the target directory.

The `ASSIGN` command is used to map logical drives, and this mapping
is persisted during reboots. See the command reference below for more info.

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

Add or edit `HistorySize=8` in `/SYS/SETTINGS.CFG` on the SD card. Valid values
are 1-20. Missing or invalid settings use 8; larger values are capped at 20.
kDOS reads this setting once, when you first enter the DOS prompt after boot.
Reboot to apply a later change.

Keys are case-insensitive; spaces around `=` and `#`/`;` comments are allowed.
If repeated, the last matching assignment wins. Use a text file smaller than
16 KiB. Read errors, a stuck BUSY response, or an oversized file fall back to
the default. 

Edit the repository's `SYS/SETTINGS.CFG` to change the build's configuration copy. 

## DOS Commands

Below is a summary of the suppoerted DOS commands. 

| Command            | Description                    | Alias                |
|--------------------|--------------------------------|----------------------|
| ASSIGN {d}:{path}  | Map virtual drive to directory |                      |
| CD {dirName}       | Set working directory          |                      |
| COPY {file} {dest} | Copy one or more files         | CP                   |
| CWD                | Display current directory      | PWD                  |
| DELETE {file}, ... | Delete one or more files       | DEL, KILL, RM, RMDIR |
| DIR {wildcard}     | display directory contents     | LS                   |
| DI                 | Disable Interrupts / RTC       |                      |
| EI                 | Enable Interrupts / RTC        |                      |
| HELP               | Display a summary of commands  |                      |
| LOAD {filename}    | Load a CMD program             |                      |
| MKDIR {path}       | Make a directory               | MD                   |
| RENAME {f1} {f2}   | rename file or directory       | REN, MOVE, MV        |

### ASSIGN

The `ASSIGN` command maps virtual drive numbers `1` through `9` to directories 
on the underlying storage volume. Once assigned, commands and file operations 
that reference `:1`–`:9` resolve relative to that mapped directory 
instead of requiring a full path every time.

Drive `:0` remains the default/current directory and cannot be reassigned via `ASSIGN`.

The current assignments are persisted in the file `/SYS/ASSIGN.CFG`

#### Syntax

```text
ASSIGN
ASSIGN <D>:<PATH>
ASSIGN <D>:
```

Usage:
* Run ASSIGN with no arguments to display all currently configured mappings:
* Run ASSIGN Specifying a drive digit (1–9), a colon (:), and a directory path to create or overwrite a mapping
* Run ASSIGN Specifying a drive digit (1-9), and a colon (with no path) to clear that virtual drive mapping

Where:
* <D>: Virtual drive digit from 1 to 9.
* <PATH>: Target directory path (for example, /DOCS or DOCS). 

#### EXAMPLES

| Command        | Description                             |
|----------------|-----------------------------------------|
| ASSIGN         | List current assigments                 |
| ASSIGN 1:/DOCS | Map the :1 drive to the /DOCS directory |
| ASSIGN 1:      | Remove the drive :1 mapping             |

### CD Command

Changes the Current Working Directory

#### Syntax

```text
CD {directory}
```
Where:
* {directory} — A directory to change to. When specifying a directory

#### Examples

| Command          | Description                     |
|------------------|---------------------------------|
| CD /             | Change to Root Directory        |
| CD /SUBDIR       | Change to Sub Directory of Root |
| CD SUBDIR        | Change to a Sub Directory       |
| CD SUBDIR/SUBSUB | Change to a Sub Sub Directory   |
| CD ..            | Change to Parent Directory      |
| CD ../OTHERDIR   | Change to Relative Directory    |

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

| Command                     | Description                        |
|-----------------------------|------------------------------------|
| COPY README.TXT README.BAK  | Single file copy with rename       |
| COPY DATA.DAT BACKUP        | Single file copy into a directory  |
| COPY DOCS/NOTES.TXT ARCHIVE | Single file copy using path prefix |
| COPY FILE.* BACKUP          | Copy qualified files to directory  |
| COPY *.TXT BACKUP           |                                    |
| COPY *.DAT *.BAK            | Copy files changeing the extension |
| COPY * BACKUP               | Copy All files to directory        |
| COPY *.* BACKUP             | Copy Files with extension to dir   |

### CWD Command

Display the current working directory. PWD is an alias for this command.

#### Syntax

```text
CWD
PWD
```

#### Example

```text
:CWD
/GAMES
:
```

### DELETE Command

Deletes one or more files non-interactively (aliases: DEL, KILL, RM, RMDIR).
Multiple space-separated filenames or wildcard patterns may be supplied in a
single command. 

When using wildcards Subdirectories, hidden/system files, and
read-only files are skipped. If these need to be deleted it will have to
be done on a modern computer.

To delete a directory you must type its exact name (no wildcards are supported)
and the directory must be empty before it can be deleted.

Using a wildcard delete such as `DEL *` is non recursive, it only deletes files,
not directories, or files in sub-directories

#### Syntax

```text
DEL {fileSpec} [,{fileSpec} ...]
```
Where:{fileSpec} — A single filename, a path with a filename, or a pattern
containing * wildcards (case-insensitive).

#### Examples

| Command               | Description                          |
|-----------------------|--------------------------------------|
| RMDIR SUBDIR          | Single directory delete              | 
| DEL TEMP.TXT          | Single file delete                   | 
| DEL FILE1.BAS SUBDIR  | Multiple files or directories        | 
| DEL *.BAK             | Delete Files with extension          | 
| DEL *                 | Delete all files                     | 
| DEL *.*               | Delete all files (with extension)    | 
| DEL TEMP/FILE1.BAS    | Delete a file in a directory         | 
| DEL TEMP/*.BAK        | Delete multiple files in a directory | 

#### Output and Errors

* Completed: Displays **N File(s) Deleted.** where N is the total number of
files deleted across all tokens (including 0 if no files matched).
* Partial delete: If an error occurs after one or more files have already
been deleted, displays **N File(s) Deleted, with Error Code.**
* Immediate failure: If no files are deleted and an error occurs (such as
an invalid name or missing target), returns a DOS error status.

### DIR Command

List files and subdirectories on the storage volume. Alias supported: `LS`.

#### Syntax

```text
DIR
DIR <PATTERN>
DIR :<D>
DIR <PATTERN>:<D>
DIR /<PATH>[/<PATTERN>]
DIR ./<PATH>[/<PATTERN>]
DIR ../<PATH>[/<PATTERN>]
```

Where
* PATTERN - Optional filename or wildcard filter (* and ?). Defaults to * (all entries).
* :D - Optional postfixed logical drive number (1–9), targets the directory mapped via ASSIGN
* /PATH: Explicit path anchored at the root directory (for example, DIR /SYS or DIR /SYS/*.SYS).
* ./PATH: Explicit path relative to the current working directory (for example, DIR ./GAMES).
* ../PATH: Explicit path relative to the parent of the current working directory (for example, DIR ../TEMP).
* :D Cannot be combined with path prefixes (/, ./, ../).

#### Examples

| Command        | Description                                  |
|----------------|----------------------------------------------|
| DIR            | List all files in current directory          |
| DIR *.BAS      | List all BAS files in current directory      |
| DIR :2         | List all files in logical drive :2           |
| DIR *.BAS:2    | List all BAS files in logical drive :2       |
| DIR /SYS       | List all files in /SYS directory             |
| DIR /SYS/*.SYS | List all SYS files in /SYS directory         |
| DIR ./GAMES    | List all files in GAMES sub-directory        |
| DIR ../GAMES   | List all files in GAMES parent sub-directory |

#### Viewing Behavior

* File names only: The listing shows entry names without file sizes.
* Subdirectories: Subdirectory entries are prefixed with a graphical vertical bar (|).
* Paged output: Long listings pause after each page—press any key to continue to the next page, or press BREAK to abort and return to the DOS prompt.
* Invalid combinations: Mixing explicit path prefixes with a logical drive suffix (such as DIR /TEMP:4) or 
  referencing an unmapped drive (:1–:9) returns a device/parameter error.

### DI EI Commands

Enable and Disable Interrupt Service Routines. 
This currently will enable or disable the Real Time Clock

#### Syntax

```text
EI
DI
```

Where:
- EI - enable interrupts
- DI - disables interrupts

### HELP Command

Displays a brief summary of available commands

#### Syntax

```text
HELP
```

### LOAD Command

Allows an executable file (CMD) to be loaded into memory, but not executed.

#### Syntax

```text
LOAD {fileSpec}
```
Where:{fileSpec} — A CMD filename to load

CAUTION: This could conflict with a BASIC program resident in memory

### MKDIR Command

Create a new directory

#### Syntax

```text
MKDIR {directory}
```

Where:{directory} — The name of the directory to create

### RENAME Command

Renames a single file or directory, moves an item to another directory, 
or batch-renames matching files using wildcards (aliases: `REN` `MOVE`, `MV`). 
Wildcard matching applies to files only; subdirectories, hidden/system files, 
are skipped during wildcard renames.

#### Syntax

```text
REN {source} {dest}
```

Where:
- {source} — A single file or directory name, a path, or a file wildcard pattern containing * (case-insensitive).
- {dest} — A new name, a target directory path, or a wildcard pattern such as *.OLD or MYWORK.*.

#### Examples

| Command                       | Description                 |
|-------------------------------|-----------------------------|
| REN OLDNAME.BAS NEWNAME.BAS   | Single file rename          |
| REN TEMP WORK                 | Directory rename            |
| MOVE GAMES /TEMP/GAMES        | Move and Rename a directory |
| MOVE FILE1.BAK TEMP/FILE2.BAK | Move file to directory      |
| REN *.BAK *.OLD               | Wildcard extension swap     |
| REN MYDB.* MYWORK.*           | Wildcard prefix mapping     |

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

Note: Ony Tokenized BAS files are supported. ASCII files will not work.

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

All of these functions work exactly as do the documented TRS-DOS
BASIC extensions, please refer to the official documentation,
or in sections below for more information.

### Descriptive Error Messages

BASIC will display the descriptive error messages.

### CMD - Calling DOS commands.

`CMD` accepts a string expression containing an internal DOS
command. It works at the BASIC prompt and inside a program. A successful
command returns to the next BASIC statement; it does not change to the DOS
prompt or discard BASIC variables.

This API does not implement all historical TRSDOS CMD subcommands.

```basic
10 CMD "PWD"
20 CMD "DIR *.BAS"
30 PRINT "BACK IN BASIC"
```

The existing internal commands and aliases are available. A command string may
contain at most 127 characters. For example, `CMD "CD GAMES"` changes the
current directory for later BASIC and DOS file operations.

Directory paging behaves as it does at the DOS prompt. BREAK at a paused
listing stops the listing and resumes BASIC without clearing the screen.

Unknown commands and external program names such as `CMD "GALAXY"` produce
`Illegal function call`. 

The DOS LOAD command such as `CMD "LOAD TEST.CMD"` loads binary records without
executing the transfer address, then continues BASIC. The binary must target
memory or banks reserved by your application; loading over BASIC or DOS can
corrupt the running system. Use BASIC's `LOAD` for BASIC programs.

BASIC translates DOS error numbers into BASIC errors. 

## BASIC Disk I/O

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

## Appendix

### DOS Error Codes

Error's are aligned to TRS-DOS errors where possible. 
The following is a list of TRS-DOS alligned errors handled by kDOS

| Error Number | Error Message             |
|--------------|---------------------------|
| 0            | No Error                  |
| 15           | Write Protected Disk      |
| 16           | Illegal File Number       |
| 19           | Illegal Filename          |
| 24           | File Not Found            |
| 28           | End of File Encountered   |
| 31           | Program Not Found         |
| 32           | Illegal Drive Number      |
| 34           | Load File Format Error    |

The following errors have been introduced by kDOS

| Error Number | Error Message             | TRS-DOS                                         |
|--------------|---------------------------|-------------------------------------------------|
| 56           | Too Many Files Open       | Exceeds maximum of 16 files                     |
| 57           | Denied, File Already Open | Try to open a File that is already open         |
| 58           | Denied, Dir Not Empty     | Try to delete a directory that is not empty     |
| 59           | File Exists               | Try to rename to, or overwrite an existing file |
| 60           | Path Not Found            | Path Not Found                                  |
| 61           | Illegal DOS Function      | A DOS feature or function that is not available |
| 62           | Internal DOS Error        | Exceptional Error that shouldn't occur.         |
| 63           | Unknown Error             | Unknown Error                                   |

## References

TRS-DOS & Disk Basic Reference v2.3
