# kDOS for the TRS-80 Model I

## Introduction

kDOS is an operating environment that runs on the Tandy TRS-80 Model 1
providing a TRS-DOS (DOS) like features to Level 2 BASIC

The DOS runs alongside Level 2 BASIC, rather than supplanting it.
Typing a DOS command and a BASIC statement are done in the
same shell.

Files are stored and accessed from SD card in a standard FAT filesystem.
There is no emulation of TRS-80 floppy disk or hard disk drives,
nor any TRS-DOS (like) file-system. 

There are no imposed file size limits, or limits on the number 
of files that can be stored, for a TRS-80 a modern SD card could be 
considered infinite storage. Directories are fully supported.
Files copied to the SD card by modern computer, are 
directly readable on the TRS-80. 

Programs that run on TRS-DOS "should" run under kDOS so long
as they use standard DOS API calls. Programs that directly 
access FDC hardware or undocumented (non-standard) API calls will 
probably not function, unless patched.

## Features

Core Features
* Modern Filesystem 
  * Files are stored natively on the FAT filesystem.
  * File directories (including nested) are supported
  * File storage space is unrestricted, can store any number of files
  * Automatic conversion of traditional filename/ext into filename.ext
* DOS Features
  * DOS commands are typed into the BASIC command shell
  * Most DOS entry points at $4400 are supported.
  * Interrupts with real Time Clock supported
* BASIC features
  * Extended Basic functions are supported
  * Long error messages ar displayed
  * Disk File IO Statements are currently NOT supported
* Has a Low memory overhead than a traditional DOS
  * Requires about 0.5Kb of main memory space.
  * Uses virtual memory from $3000-$37DF
  * 47800 Bytes Free, compared with 48350 on Level 2 BASIC 
  * Memory from $4500 is available for application usage.

## Components

This solution requires:
* Model 1 computer with 16K (or 48k) RAM
* Floppy80 for Model 1 board for storage.
* SD Card for OS and user file storage.
* Expansion Interface is NOT required

While the Floppy 80 is the primary hardware required by this solution,
the FreHD is supported in a very basic form, mainly for emulation 
and testing purposes

## Operation and Use

See the Seperate [Quick Start](./QUICKSTART.md) for a getting started,
and the full [User Guide](./USERGUIDE.md) for detailed operation

## Work In Progress

This is a work in progress not all features are implemented at this time.
Please use it at your own risk.
See the separate ![Compatibility](./SYS/DOC/COMPATIBILITY.md) document 
for what is and isn't supported.

## References

### Floppy80

The [Floppy80-M1](https://github.com/MichaelM4/Floppy80-M1) project 
provides the hardware design on which this project relies. 
Any PCB can be used which conforms to this specification can be used. 
Other notable designs include.
* [Model 1K Floppy 80](https://github.com/kiwisincebirth/TRS-80-MODEL-1-K/tree/main/floppy80)

### Floppy90

The companion [Floppy90](https://github.com/kiwisincebirth/Floppy90) project 
provides the Firmware that runs on the RP2350. In summary, it provides 
* A command API similar to (but a superset of) FreHD, to provide needed File capabilities.
* 256KB of Banked Memory (in the $3000 - $37FF memory region)
* Optional 32 Kb of High Memory, for use in 16KB machines
* Support for loading a Boot sector at startup

## Credits

Thanks to the following for supporting and aiding in this project
- @dusty2050 for his code contributions to this project
- The Tandy Discord Channel for feedback, help and support
