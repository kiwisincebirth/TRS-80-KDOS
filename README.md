# kDOS for the TRS-80 Model I

## Introduction

kDOS is a operating environment that runs on Model 1 providing
a TRS-DOS (DOS) like features to Level 2 basic

The DOS runs alongside BASIC, rather than supplanting it.
Typing a DOS command and a BASIC statement are done in the
same shell.

Files are stored on SD card in native FAT filesystem.
There is no emulation of legacy floppy or hard disks,
nor any TRS-DOS (like) file-system. 

There are no meaningful limits (SD card size) on the number 
of files that can be stored. Directories are fully supported.
Files copied to the SD card in modern computer, are 
directly readable on the TRS-80

Programs that run on TRS-DOS "should" run under kDOS so long
as they use standard DOS calls.

## Features

Core Features
* Supportive for existing Hardware
  * Floppy-80 (Model1) with custom PiPico V2 firmware. This is the preferred option
  * FreHD - In a basic very basic form. This is supported mainly for emulation and testing purposes
* Modern Filesystem features including
  * Files are stored natively on the FAT filesystem.
  * File directories are supported, (currently 1 directory at a time)
* DOS Features
  * DOS commands are typed into the BASIC command shell
  * Most DOS entry points at $4400 are supported.
  * Interrupts with real Time Clock support
* BASIC features
  * Extended basic functions (non IO) are supported
  * Basic File IO Statements are not supported
  * Long error messages ar displayed
* Has a Low memory overhead than a traditional DOS
  * Requires about 0.5Kb of main memory space.
  * 48350 on Level 2 -> - 47800 on Pico (550 bytes less)  

## Components

This solution requires:
* Model 1 computer with 16K (or 48k) RAM
* Floppy 80 - M1 hardware, (optional FreHD hardware)
* SD Card for file storage.
* Expansion Interface is NOT required

* The solution provides
* Software that runs on TRS-80, provides DOS like features
  * software is stored and loaded fom SD card 
* Software that runs on RP Pico v2 RP2350 that 
  * provides interfaces with Z80 code,
  * provides services to expose filesystem
  * provides 128 Kb of virtual memory
  * provides 32 Kb of High Memory (optional)

The Floppy 80 is the primary hardware required by this solution. Custom Firmware provides
* A command API similar to (but a superset of) FreHD, to provide needed DOS capabilities.
* Paged Memory (in the $3000 - $37DF memory region), for low DOS overhead
* A Floppy Disk emulation (only) to support the loading of a boot block at start

## Supported

|              | Floppy 80            | Caveat                     |      |
|--------------|----------------------|----------------------------|------|
| BASIC        | LOAD "filename.BAS"  | Load a basic Program       | All  |
| Commands     | SAVE "filename.BAS"  |                            | All  |
|              | RUN "filename.BAS"   |                            | All  |
|              | KILL "filename"      | Delete a file (todo)       | Pico | 
|              | MERGE "filename"     | Merge a file (todo)        | Pico | 
|              | -                    |                            |      |
| BASIC        | &Hxx                 | Hexadecimal Constant       | Pico |
| Instructions | &Oxx                 | Octo-decimal Constant      | Pico |
|              | DEF FNn(A)=A         | Define a User Function     | Pico |
|              | DEF USRn=ADDR        | Define a Call address      | Pico |
|              | FNn(A)               | Invoke a User Function     | Pico |
|              | LINE INPUT A$        | Input an entire line       | Pico |
|              | MID(X$,N,N)=""       | Mid String Assignment      | Pico |
|              | INSTR(X$,Y$)         | String Search function     | Pico |
|              | TIME$                | RTC Current DateTime       | Pico |
|              | USRn(A)              | Invoke a Call address      | Pico |
|              |                      |                            |      |
| BASIC Errors | Display Full Error   |                            | Pico |
|              |                      |                            |      |
| DOS          | #filename            | Runs a CMD program         | All  |
|              | #CD {dirName}        | Set working directory      | Pico |
|              | #COPY {f1} {f2}      | Copy a File                | Pico |
|              | #DEL {filename}      | delete file or directory   | Pico |
|              | #DIR {wildcard}      | display directory contents | All  |
|              | #LOAD {filename.CMD} | Load a CMD program         | All  |
|              | #MKDIR {dirname}     | Make a directory           | Pico |
|              | #MOVE {f1} {f2}      | move file or directory     | Pico |
|              | #PWD                 | display current directory  | Pico |
|              | #REN {f1} {f2}       | rename file or directory   | Pico |

## Technical

### Startup

At startup holding the <CLEAR> key will :
* Disable Virtual RAM and instead use Liner Overlay RAM. 
* Reduce available ram by 512 bytes needed for overlay loading
* Disable Extended basic features, which require virtual memory.
* Disable any AUTO processing

### Boot Process

|            | Floppy 80 M1            | F80 & FHD              | FreHD                       |
|------------|-------------------------|------------------------|-----------------------------|
| ROM        | Uses a Standard L2 ROM  | ->                     | Requires FreHD Autoboot ROM |
| ROM        | Loads Floppy Boot Block | ->                     | Loads FreHD Boot Block      |
| ROM        | (BOOT.SYS loaded $4200) | BOOT.SYS loaded $5000  | FreHD boot loaded to $5000  |
| Boot Block |                         |                        | Loads FREHD.ROM             |
| Boot Block |                         |                        | -aka- BOOT/CMD to $5200     |
| Boot.SYS   | Relocates to $5200      | <-                     |                             |
| Boot.SYS   | Detects Hardware        | <-                     | Detects Hardware            |
| Boot.SYS   | Loads /SYS/SYSP.SYS     | <-                     | Loads /SYS/SYS0.SYS         |
| SYS0.SYS   | SYSP Starts at $5400    | <-                     | SYS0 Starts at $5400        |
| Overlays   | -included in SYSP-      | <-                     | Loads /SYS/SYS(A-Z).SYS     |

* BOOT.SYS - 256 byte binary image, with ORG = $6000 
* FreHD.ROM - is a direct copy of BOOT.SYS in CMD format 
* SYSP.SYS - Enhanced PICO full DOS, using virtual memory 
* SYS0.SYS - FreHD Limited version (same source code)
* Overlays are pre-loaded into Pages RAM, not dynamically
  * Are preloaded into Paged RAM as part of SYSP on Floppy80
  * Are loaded (on demand) into normal RAM, like a normal DOS

### DOS Memory Map

The high level Memory map

| Address     | Contents               | For FreHD            |
|-------------|------------------------|----------------------|
| 3400 - 3600 | DOS Overlay Area       | Moved to 4500-4700   |
| 3600 - 37E0 | DOS Loader Utility     | In Overlay Code      |
|             | RTC Clock Interrupt    | Not Supported        |
| 4000 - 41E8 | As per Level 2 Basic   |                      |
| 41E8 - 42E8 | String CMD Line Buffer |                      |
| 42E0 - 43E0 | DOS Resident Code 1    |                      |
| 43E0 - 4400 | System FCB Buffer      |                      |
| 4400 - 4480 | DOS Entry Points       |                      |
| 4480 - 44D0 | DOS Resident Code 2    |                      |
|             |                        | 4500 - 4700 Overlays |
| 44D0        | BASIC Program Start    | 4700 - Basic Program |

DOS Entry Points (4400-4480)

| Address |        | Contents                   | Issues          |
|---------|--------|----------------------------|-----------------|
| 402D    |        | No Error DOS Exit (44400)  |                 |
| 4400    | @CMD   | No Error DOS Exit          |                 |
| 4405    | @CMNDI | Execute CMD and Exit       | (Same as 4400)  |
| 4409    | @ERROR | Exit and Display Error     |                 |
| 440D    | @DEBUG | Debug Mode                 | Not Implemented |
| 4410    | @ADTSK | Add Interrupt Task         | Not Implemented |
| 4413    | @RMTSK | Remove Interrupt Task      | Not Implemented |
| 441C    | @FSPEC | Extract File Spec          |                 |
| 4420    | @INIT  | Create or Open File        |                 |
| 4424    | @OPEN  | Open Existing File         |                 |
| 4428    | @CLOSE | Close a File               |                 |
| 442C    | @KILL  | Delete an Open File        |                 |
| 4430    | @LOAD  | Load Program               |                 |
| 4433    | @RUN   | Load and Run Program       |                 |
| 4436    | @READ  | Read from Disk File        |                 |
| 4439    | @WRITE | Write to Disk File         |                 |
| 443C    | @VER   | Write and Verify           | (Same as 4339)  |
| 443F    | @REW   | Position File to Start     |                 |
| 4442    | @POSN  | Position File              |                 |
| 4445    | @BKSP  | Backspace Fle 1 Record     |                 |
| 4448    | @PEOF  | Position File to EOF       |                 |
| 4467    | @DSPLY | Display a String           |                 |
| 446A    | @PRINT | Print a String             |                 |
| 446D    | @TIME  | Time into (HL) buffer      | todo            |
| 4470    | @DATE  | Date into (HL) buffer      | todo            |
| 4473    | @FEXT  | Default Filename extension |                 |

; todo should we insert these int table below
; (400C) RST 28H DOS Supervisor Call Dispatcher     
; (400F) RST 30h (DOS DEBUG entry point) Vector.
; (4012) RST 38h (Interrupt Service) Vector.                                                                                                 
; (4033) DOS Char I/O Driver for Disk Files
; (4427) * ND8Ø $82 identifying ND(8)0v(2)                                        
; (442B) * ND8Ø $Ø1 if Model I and $Ø3 if Model III.

### Floppy 80

#### Hardware Address Map

The following is provided by the RP2350 Pico Hardware

| Address     |                                 |
|-------------|---------------------------------|
| 3000 - 3400 | Virtual Memory (page entry)     |
| 3400 - 3600 | Virtual Memory (page swappable) |
| 3600 - 37E0 | Scratch Memory (static)         |
| 37E0        | Read and Reset RTC Interrupt    |
| 37EC        | FDC Command Status              |
| 37EF        | FDC Data Register               |
| 37F0        | Virtual Memory Page Register    |
| IO Port $C2 | Pico DATA IO Port               |
| IO Port $C3 | Pico SIZE Register              |
| IO Port $C4 | Pico COMMAND Register           |
| IO Port $C5 | Pico ERROR Register             |
| IO Port $CF | Pico STATUS Register            |

## Caveats

### Work In Progress
This is a work in progress not all features are implemented at this time.
See the separate Compatibility document for what is and isn't supported.

### FreHD solution
* Only provides a small sub set of functions (frehd limited firmware)
* Consumes 512 bytes more RAM for overlays (no paged ram)
* file management, and sub-Directories are not supported
* Many DOS API's (support File IO) are not supported
* Doesn't support Disk Basic extensions.

# DEV NOTES

### Todo 
* FIRMWARE - STAatus command display Virtual Paging Info
* FIRMWARE - STAatus command display Heap size remaining
* FIRMWARE - Reset Signal is not resetting the ROOT folder, left in sub folder.

### Issues
* typing LOAD "xx.bas" (basic command) from DOS causes a hang
* running a program that has no END $ADDRESS - will run code based on last byte loaded - crash.
  * instead this should be detected and generate an error

### Keyboard
Good Keyboard Driver e.g. LDOS, interrupt driven e.g. support typeahead
* keyboard @ key has the caps lock behaviour, it shoudn't.
* keyboard Shift @ key doesnt respont frequently, only every second keystroke.

### Improvement
* Improve the code addition of .CMD to a filename when executing from CMD processor.
  * When using LOAD SAVE RUN "file/BAS:N" /BAS could be added if not specified

### RTC
* Full reboot should not wipe out Clock, needs secondary storage.
  * maybe just define an API on Pico to get time, and maintain it there
  * existing SYS 0 static defines should be removed
  * copied on boot into RAM

### Improvement - Error handling
* #RM BASIC - removing a directory (not empty) produced "FF Error 7" Access denied due to prohibited
  access or directory full -> Should provide better error.
* #MKdir BASIC - FF Error 8 - Exists
* Need "Access Denied" and "Exists" messages - but maybe 
  * in RM we MAP the Access Denied to "Directory Not Empty"
  * in MKDIR we MAP the Exists     to "Directory Exists"

### PicoRAM
* Need to investigate the Enhanced Flag ???
* Remove the ENHANCED runtime variable directive ???
* Conditional Build directives #IFDEF FREHD_BUILD
* Need to build 2 sets of artifacts - 1 for Frehd overlays, and 1 for PicoRam

### High Priority
* M1ZVM
* Debugger

### DOS Entry Points
Need to add these
* Date Time
  * (446D) @TIME todo Get the time "23:59:59" into (HL)
  * (4470) @DATE todo Get the date "12/12/99" into (HL)
* Filename Extension

### Medium
* Add a #COPY file.ext:N file.ext:N command
* Add a KILL basic statement, leveraging #DELETE
* Add a MERGE basic statement
* Add BASIC FILE IO statements
* #DIR {optional: wildcard}{optional :dirNumber} - List contents of :0 or :1 - :9 -> rewrite

### Features
* Add ability for search paths when looking for file.
* Add ability for named directories :1 to :9
* NewDos 80 #System like command to store configuration parameters
* When Pressing RESET (NMI), ROM drops back to DOS Ready, 
  * Probably requires updated ROM, since cold start immediately overites $4000 - $405D
  * these addresses contan the clock and 402d dos reentry.
  * Updated Rom could check for Flag and drop to 402D
  * Boot loader cold detect existing install, look for BYTE in (KBROWCLR EQU $41E5)
  * Not load the full O/S - Paged Ram doesnt need to be touched.
  * 

### Low Priority Commands
* #HELP command
* #AUTO - startup command execution
* #APPEND - one file to another
* #REBOOT 
* #Status - display something about the Environment, implies some config to view/modify
* #Ver - something about the DOS build # Pico Build #
* #CLOSEALL - to close open file handles

# Other Docs

Features

Single Selectable Directory

using a CD command we can change the directory of the effective Drive (0).
For most file operations e.g. DIR the default is the selected drive 0

Named Virtual Directories

Defined as volume identifiers on existing File name e.g. :1 thru :9

When a file is specified with a Drive :1 - :9 then  virtual dive will be used

Several directories can be specified that allow a virtual search path
maning if not fund on :0 will search other drives in order to find it.

Static config can be used for defining these virtual
DIR1=namedDirectory1 ...
DIR9=namedDirectory9

BASIC

# Virtual Memory

| Calling Code | Springboard  | Exit From VM | Unwind of the Virtual Page                   | Call Stack |     | 
|--------------|--------------|--------------|----------------------------------------------|------------|-----|
| JUMP         | JUMP         | JUMP         | GOOD. No expectation of unwind               | GOOD       | A   |
| JUMP         | JUMP         | RET          | ** OK. Expectation of unwind                 | GOOD       | C - |
| JUMP         | CALL (push)  | JUMP         | ** BAD **                                    | ** BAD **  | F-  |
| JUMP         | CALL (push)  | RET          | GOOD. Normal Ret from routine as final line  | GOOD       | A # |
| CALL         | JUMP         | JUMP         | ** OK. Future ret will bypass the unwind     | GOOD       | C   |
| CALL         | JUMP         | RET          | ** OK. Bypass unwind of Virtual Memory       | OK         | C - |
| CALL         | CALL (push)  | JUMP         | GOOD. Normal Call, future ret will unwind VM | GOOD       | A   |
| CALL         | CALL (push)  | RET          | GOOD. Normal Call/Ret pttern                 | GOOD       | A # |

Call to a Routine that Returns Only -> Make it a CALL
Call to a routine that Jumps Only   -> Make it a CALL
Call to a routine that RETs or JPs  -> Make it a CALL

Jump to a Routine that Returns Only -> Make it a CALL
Jump to a routine that jumps   Only -> Make it a Jump
Jump to a routine that RETs or JPs  -> Make it a Jump

# Filenames

## Enhanced Filename & Path Handling

The DOS features a filename and path sanitiser that allows the TRS-80 to interact with a modern SD card.
This system supports both legacy TRS-DOS naming conventions and modern hierarchical FAT subdirectories.

### Core Features
* **Legacy Support:** Automatically translates the classic `FILENAME/EXT` syntax into modern `FILENAME.EXT` format.
* **Modern Pathing:** Supports standard FAT subdirectories (e.g., `GAMES/ACTION/ZAXON`).
* **Automatic Sanitization:** All filenames are automatically converted to uppercase and stripped of non-compatible characters.
* **Drive Mapping:** Use the `:D` suffix (0-9) to quickly access different "Mount Points" or directories configured on your SD card.
* **Password Stripping:** Automatically ignores the `.PASSWORD` suffix used in some legacy software, ensuring compatibility without manual file renaming.

### Some Examples

| Input Pattern       | Logic Applied        | Resulting Behavior                                          |
|:--------------------|:---------------------|:------------------------------------------------------------|
| `name.bas`          | **Case Insensitive** | File names are converted to uppercase e.g. `NAME.BAS`       |
| `NAME/BAS`          | **Legacy Ext**       | Single slash with 1-3 chars are converted `NAME.BAS`        |
| `/SYS/SYS0.SYS`     | **Absolute Path**    | Direct path from SD root.                                   |
| `../DIR/FILE.BAS`   | **Relative Path**    | Leading dots are preserved; slashes treated as directories. |
| `EDIT/ASM/CMD`      | **Hybrid File**      | Handles the Path and legacy extension `EDIT/ASM.CMD`        |
| `FILE.TXT:1`        | **Drive Map**        | `:1` is extracted as Drive ID 1 and removed from path.      |
| `F.PASS` (4+ chars) | **Password**         | Treated as legacy password; string is truncated.            |
| `F.PAS` (1-3 chars) | **Modern Ext**       | Treated as valid modern extension; extension is preserved.  |

### Filenames

The following inputs all result in the same FAT filename CONFIG.SYS:
* CONFIG.SYS (Modern FAT style)
* config.sys (User typing in lowercase)
* CONFIG/SYS (Legacy TRS-DOS style)
* CONFIG/SYS.PASSWORD (Legacy with password ignored)
