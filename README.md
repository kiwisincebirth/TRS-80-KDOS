# MiniDOS for the TRS-80 Model I

## Introduction

Mini DOS is a minimalistic DOS (TRS-DOS supportive) that runs on
a Model 1 computer which has native support for FAT filesystem

Programs that run on TRS-DOS should run under MiniDOS so long
as they use standard DOS calls.

The DOS runs in the Level 2 Basic command Shell, and dos
commands are executed using the `#` prefix. e.g.

`#DIR`

## Features

Core Features
* Supportive for existing Hardware
  * Floppy-80 (Model1) with custom PiPico V2 firmware. This is the preferred option
  * FreHD - In a basic very basic form. This is supported mainly for emulation and testing purposes
* Runs in the BASIC command shell
* DOS Features
  * Most DOS entry points at $4400 are supported. 
* BASIC features
  * Disc Basic Features are supported
  * Long error messages ar displayed
* Modern features including 
  * Files are stored natively on the FAT filesystem.
  * File directories are supported, (currently 1 directory at a time)
* Has a Low memory overhead than a traditional DOS
  * Requires about half a KB of main memory space.
  * 48350 on Level 2 -> - 47800 on Pico (550 bytes less)  

## Floppy 80

The Floppy 80 is the primary hardware required by this solution. Custom Firmware provides
* A command API similar to (but a superset of) FreHD, to provide needed DOS capabilities.
* Paged Memory (in the $3000 - $37DF memory region) to allow for
* A Floppy Disk emulation (only) to support the loading of a boot block at start

The FreHD solution
* Only provides a sub set of functions as It's firmware has not been evolved.
* Consumes more RAM (512KB) for overlays as doesnt have paged memory.
* Doesnt support Disk Basic functions.

## Components

* Model 1 computer with 16K (or 48k) RAM
* DOS components (Z80 code) running on Model 1
* Custom Firmware (written in C) that Runs on Pi Pico V2
* SD Card for storage
* Expansion Interface is not needed

## Spported

|              | Floppy 80           | Caveat                |
|--------------|---------------------|-----------------------|
| BASIC        | LOAD "filename.BAS" |                       |
| Commands     | SAVE "filename.BAS" |                       |
|              | RUN "filename.BAS"  |                       |
|              | -                   |                       |
| BASIC        | &Hxx                | Hexidecimal Constant  |
| Instructions | &Hxx                | Octodecimal Constant  |
|              | MID(X$,N,N)=""      | Mid String Assignment |
|              | INSTR(X$,Y$)        | String Searh          |
|              |                     |                       |
| DOS          | #filename           | Runs a CMD program    |
|              | #LOAD filename.CMD  | Load a CMD program    |
|              |                     |                       |
| DOS          | #DIR *.*            |                       |
|              | #CD                 |                       |
|              |                     |                       |


## Technical

### Boot Process

|            | Floppy 80                  | F80 & FHD                | FreHD                      |
|------------|----------------------------|--------------------------|----------------------------|
| ROM        | Uses a Standard L2 ROM     | ->                       | Requires FreHD Autoboot ROM |
| ROM        | Loads Floppy Boot Block    | ->                       | Loads FreHD Boot Block     |
| ROM        | (BOOT.SYS loaded to $4200) | BOOT.SYS loaded to $5000 | FreHD boot loaded to $5000 |
| Boot Block |                            |                          | Loads FREHD.ROM            |
| Boot Block |                            |                          | -aka- BOOT/CMD to $5200    |
| Boot.SYS   | Relocates to $5200         | <-                       |                            |
| Boot.SYS   | Detects Hardware           | <-                       | Detects Hardware           |
| Boot.SYS   | Loads /SYS/SYS0P.SYS       | <-                       | Loads /SYS/SYS0F.SYS       |
| SYS0.SYS   | Starts at $5400            | <-                       | Starts at $5400            |
| Overlays   | -included in SYS0P-        | <-                       | Loads /SYS/SYS(A-Z).SYS    |

* BOOT.SYS - 256 byte binary image, with ORG = $6000 
* FreHD.ROM - is a direct copy of BOOT.SYS in CMD format 
* SYS0P.SYS - Enhanced PICO full DOS Version 
* SYS0F.SYS - FreHD Limited version (same source code)
* Overlays are pre-loaded into Pages RAM, not dynamically
  * Are preloaded into Paged RAM as part of SYS0 on Floppy80
  * Are loaded (on demand) into normal RAM, like a normal DOS

### Memory Map

| Address     | Contents               | For FreHD               |
|-------------|------------------------|-------------------------|
| 3400 - 3600 | DOS Overlay Area       | Located at 4500-4700    |
| 3600 - 37E0 | DOS Loader Utility     | Moved into Overlay Code |
| 4000 - 41E8 | As per Level 2 Basic   |                         |
| 41E8 - 42E8 | String CMD Line Buffer |                         |
| 42E0 - 43E0 | DOS Resident Code 1    |                         |
| 43E0 - 4400 | System FCB Buffer      |                         |
| 4400 - 4480 | DOS Entry Points       |                         |
| 4480 - 4500 | DOS Resident Code 2    |                         |
| 4500 -      | BASIC Program Start    | Raised to 4700          |


## Caveats

This is a work in progress not all features are implemented at this time.
See the separate Compatibility document for what is and isn't supported.

## Todo
* FIRMWARE - STAatus command display Paging Info 
* FIRMWARE - Create a loader for the Boot.SYS startup block into FDC boot
* FIRMWARE - create a floppy FDC loader for Boot.SYS at $4200

### Issues

### Improvment
* Improve the code addition of .CMD to a filename when execuing from CMD processor.
  * When using LOAD SAVE RUN "file/BAS:N" /BAS could be added if not specified
* OverlayB for basic save load etc, should error out if can locate the command
* FreHD DIR should not display directories

### PicoRAM
* Need to investigate the Enhanced Flag
* Need to build 2 sets of artifacts - 1 for Frehd overlays, and 1 for PicoRam
* Conditional Build directives #IFDEF FREHD_BUILD
* Remove the ENHANCED runtime variable directive

### High Priority
* DIR {optional :dirNumber} - List contents of :0 or :1 - :9 -> rewrite
* CD {nameOfDirectory or /} - Sets an implicitly named directory as :0
* Add a #CD command (PICO)

### DOS Entry Points
* InitFile / OpenFile
* CloseFile
* ReadFile / WriteFile
* Rewind / BackSpace / Skip / EOF

### Medium
* Add a #COPY file.ext:N file.ext:N command
* Add a #DEL file/ext:N - KILL "" (basic) command
* Add a #MKDIR command
* MKDIR {nameOfDirectory}
* Add a #REN command
* RENAME file/ext:N file/ext:N
* Add ability for search paths when looking for file.
* Add ability for named directories :1 to :9

### Low Priority Commands
* Add a #HELP command
* AUTO - startup command execution
* APPEND - one file to another
* Boot
* Status
* Ver

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


