
# Quick Start 

## Introduction

kDOS is an operating environment that runs on the Tandy TRS-80 Model 1
providing a TRS-DOS (DOS) like features to Level 2 BASIC

## Requirements

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

Install the RP2350 firmware (from /SYS/FIRMWARE) onto the (RP2350) Floppy-80 M1

## Usage

Once started you should see the message "kDOS Loaded", and be dropped into a BASIC
"READY>" Prompt. On a modern Enhanced L2 ROM

```
Enhanced Level II BASIC
Release 1.4
47,294 Free Bytes
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

Pressing "ENTER" (without typing a command) will switch to the 
DOS ":" prompt. To get a summary of DOS commands type the command "HELP"

```
READY
>
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

Typing DIR will list contents of the drive.

