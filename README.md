# MiniDOS for the TRS-80 Model I

## Introduction

Mini DOS is a minimalistic DOS (TRS-DOS supportive) that runs on
a Model 1 computer which has native support for FAT filesystem

Programs that run on TRS-DOS should run under MiniDOS so long
as they use standard DOS calls.

The DOS runs in the Level 2 Basic command Shell, and dos
commands are executed using the `#` prefix. e.g.

`#DIR *.*`

## Features

Core Features
* Supportive for existing Hardware
  * Floppy-80 (Model1) with custom PiPico V2 firmware. This is the preferred option
  * FreHD - In a basic very basic form. This is supported mainly for emulation and testing purposes
* Runs in the BASIC command shell
* DOS Features
  * Most DOS entry points at $4400 are supported.
  * Interrupts with real Time Clock support
* BASIC features
  * Disc Basic Features are supported
  * Long error messages ar displayed
* Modern Filesystem features including 
  * Files are stored natively on the FAT filesystem.
  * File directories are supported, (currently 1 directory at a time)
* Has a Low memory overhead than a traditional DOS
  * Requires about half a KB of main memory space.
  * 48350 on Level 2 -> - 47800 on Pico (550 bytes less)  

## Components

This solution requires the following
* Model 1 computer with 16K (or 48k) RAM
* Floppy 80 M1 hardware, optionally FreHD hardware
* Custom Firmware (written in C) that Runs on Pi Pico
* SD Card for file storage, containing the O/S files.
* Expansion Interface is NOT required

## Floppy 80

The Floppy 80 is the primary hardware required by this solution. Custom Firmware provides
* A command API similar to (but a superset of) FreHD, to provide needed DOS capabilities.
* Paged Memory (in the $3000 - $37DF memory region), for low DOS ovrhead
* A Floppy Disk emulation (only) to support the loading of a boot block at start

### Hardware Address Map

The following is provided by the Pic Hardware

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

## Supported

|              | Floppy 80            | Caveat                     |      |
|--------------|----------------------|----------------------------|------|
| BASIC        | LOAD "filename.BAS"  | Load a basic Program       | All  |
| Commands     | SAVE "filename.BAS"  |                            | All  |
|              | RUN "filename.BAS"   |                            | All  |
|              | KILL "filename"      | Delete a file (todo)       | Pico | 
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

### Memory Map

The effective Memory map

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

; todo should we insert these int table below
; (400C) RST 28H todo investigate BREAK Break Key; DOS Supervisor Call Dispatcher     
; (400F) RST 30h (DOS DEBUG entry point) Vector.
; (4012) RST 38h (Interrupt Service) Vector.                                                                                                 
; (4033) DOS Char I/O Driver for Disk Files
; (4427) * ND8Ø $82 identifying ND(8)0v(2)                                        
; (442B) * ND8Ø $Ø1 if Model I and $Ø3 if Model III.

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
| 4473    | @FEXT  | Default Filename extension | todo            |
| 44      | @      |                            |                 |
| 44      | @      | - tbc -                    |                 |
| 44      | @      |                            |                 |
| 447E    |        | DOS Major Version          |                 |
| 447F    |        | DOS Minor Version          |                 | 

## Caveats

### Work In Progress
This is a work in progress not all features are implemented at this time.
See the separate Compatibility document for what is and isn't supported.

### FreHD solution
* Only provides a small sub set of functions as he frehd firmware has not been evolved.
* Consumes more RAM (512KB) for overlays as doesnt have paged memory.
* Doesnt support Disk Basic functions.

# DEV NOTES

## Todo 
* FIRMWARE - STAatus command display Virtual Paging Info
* FIRMWARE - STAatus command display Heap size remaining
* FIRMWARE - Reset Signal is not resetting the ROOT folder, left in sub folder.

### Issues
* Pico DIR command on directories to  Apple resource extensions e.g. INFO
* Typing something at command prompt and pressing <BREAK> does weird thing, 
  * Displays an FC error in FreHD Mode
  * Selects Page 225(unused) in the Page/Overlay - Doesnt Exist
  * weeird openFile(+Memory Size messages in Pico CLI
* Pressing BREAK during basic program does not stop the program
  * Pico - Doest stop the program
  * FreHD - drops on FC Error

### Improvement
* Improve the code addition of .CMD to a filename when executing from CMD processor.
  * When using LOAD SAVE RUN "file/BAS:N" /BAS could be added if not specified
* FreHD DIR should not display directories, since there is no #CD command.

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
* Add a COMMAND # just (#) which drops to # prompt, enter returns
  * Should re reentrant, so remember its state (held in $4200 RAM)

### DOS Entry Points
These are only available on PICO enabled systems
* Date Time
* Filename Extension

### Medium
* Add a #COPY file.ext:N file.ext:N command
* Add a KILL basic statement, leveraging #DELETE
* Add BASIC FILE IO statements
* #DIR {optional: wildcard}{optional :dirNumber} - List contents of :0 or :1 - :9 -> rewrite

### Features
* Good Keyboard Driver e.g. LDOS, interrupt driven e.g. support typeahead
* Add ability for search paths when looking for file.
* Add ability for named directories :1 to :9
* NewDos 80 #System like command to store configuration parameters
* When Pressing RESET (NMI), ROM drops back to DOS Ready, requires updated ROM.
  * Boot loader cold detect existing install, looking for a clue in $3600
  * rather than start running in >$5000 it could be located in Virtual RAM? (FreHD?)
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

MDOS features a filename and path sanitiser that allows the TRS-80 to interact with a modern SD card.
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
