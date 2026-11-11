# User Guide

## Startup

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

| Command         | Description                   |       |
|-----------------|-------------------------------|-------|
| {filename}      | Runs a CMD program            | FreHD |
| CD {dirName}    | Set working directory         |       |
| COPY {f1} {f2}  | Copy a File (todo)            |       |
| DEL {filename}  | delete file or directory      |       |
| DIR {wildcard}  | display directory contents    | FreHD |
| DI              | Disable Interrupts / RTC      | FreHD |
| EI              | Enable Interrupts / RTC       | FreHD |
| HELP            | Display a summary of commands | FreHD |
| LOAD {filename} | Load a CMD program            | FreHD |
| MKDIR {dirname} | Make a directory              |       |
| MOVE {f1} {f2}  | move file or directory        |       |
| PWD             | display current directory     |       |
| REN {f1} {f2}   | rename file or directory      |       |

### DIR Command

At a paused `DIR` listing, press **BREAK** to return to the DOS prompt while
keeping the displayed filenames. Any other key continues the listing. The
remaining Pico directory records are consumed silently before returning.

## BASIC Extensions

As well as the DOS commands, BASIC itself has been upgraded with
the non-disk I/O statements and extensions. The following are supported

|            | Command             | Description            |       |
|------------|---------------------|------------------------|-------|
| Commands   | LOAD "filename.BAS" | Load a basic Program   | FreHD |
|            | SAVE "filename.BAS" | Save a program to Disk | FreHD |
|            | RUN "filename.BAS"  | Load and Run a program | FreHD |
|            | KILL "filename"     | Delete a file          |       | 
|            | MERGE "filename"    | Merge a file (todo)    | FreHD | 
|            | -                   | -                      |       |
| Statements | &Hxx                | Hexadecimal Constant   |       |
|            | &Oxx                | Octo-decimal Constant  |       |
|            | CVI CVS CVD         | Convert from String    |       |
|            | DEF FNn(A)=A        | Define a User Function |       |
|            | DEF USRn=ADDR       | Define a Call address  |       |
|            | FNn(A)              | Invoke a User Function |       |
|            | INSTR(X$,Y$)        | String Search function |       |
|            | LINE INPUT A$       | Input an entire line   |       |
|            | MID(X$,N,N)=""      | Mid String Assignment  |       |
|            | MKI$ MKS$ MKD$      | Convert to String      |       |
|            | TIME$               | RTC Current DateTime   |       |
|            | USRn(A)             | Invoke a Call address  |       |

As well as this BASIC will display the descriptive error messages.
Disk Basic I/O function are a future feature

## Filenames

Files names (including directories) should follow the 8.3 naming convention.
Longer file names will be truncated to 8.3 format. While this is supported
it is not recommended as the '~' character is not consistently displayed
or available on the standard keyboard.

When entering filenames the preference is to use a modern format.
e.g. FILENAME.EXT , but the tradition format of FILENAME/EXT
is generally supported within constrains e.g. PATH/FILENAME/EXT
will be interpreted as PATH/FILENAME.EXT
