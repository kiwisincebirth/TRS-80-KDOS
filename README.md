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
* Runs in the BASic command shell
* DOS Features
  * Most DOS entry points at $4400 are supported. 
  * Disc Basic Features are supported (Floppy-80 only)
* Modern features including 
  * Files are stored natively on the FAT filesystem.
  * File directories are supported, (currently 1 directory at a time)
* DOS has a Low memory overhead than a traditional DOS
  * Requires Between 0.5 kb and 1.25 Kb main memory space.
  * 48338 on Level 2 -> - 47798 on Pico (540 bytes) -> FreHD 512 bytes less  

## Floppy 80

The Floppy 80 is the primary hardware required by this solution. Custom Firmware provides
* A command API similar to (but a superset of) FreHD, to provide needed DOS capabilities.
* Paged Memory (in the $3000 - $37DF memory region) to allow for
* A Floppy Disk emulation (only) to support the loading of a boot block at start

The FreHD solution
* Only provides a sub set of functions as It's firmware has not been evolved.
* Consumes more RAM as doesnt have paged memory

## Components

* Model 1 computer with 16K (or 48k) RAM
* DOS components (Z80 code) running on Model 1
* Custom Firmware (written in C) that Runs on Pi Pico V2
* SD Card for storage
* Expansion Interface is not needed


## Technical

### Boot Process

|            | Floppy 80                   | F80 & FHD ROM  | FreHD                        |
|------------|-----------------------------|----------------|------------------------------|
| ROM        | Requires a Standard L2 ROM  | ->             | Requires FreHD Autoboot ROM  |
| ROM        | Loads Floppy Boot Block     | <-             | Loads FreHD Boot Block       |
| ROM        | (BOOT.SYS loaded to $4200)  | BOOT.SYS $5000 | (Firmware loaded to $5000)   |
| Boot Block |                             |                | Loads FREHD.ROM              |
| Boot Block |                             |                | -aka- BOOT/CMD to $5200      |
| Boot.SYS   | Relocates to $5200          | <-             |                              |
| Boot.SYS   | Detects Hardware            |                | Detects Hardware             |
| Boot.SYS   | Loads /SYS/SYS0P.SYS        |                | Loads /SYS/SYS0F.SYS         |
| SYS0.SYS   | Starts at $5400             |                | Starts at $5400              |
| Overlays   | -included in SYS0P-         |                | Loads /SYS/SYS(A-Z).SYS      |

* BOOT.SYS - 256 byte binary image, with ORG = $6000 
* FreHD.ROM - is a direct copy of BOOT.SYS in CMD format 
* SYS0P.SYS - Enhanced PICO full DOS Version 
* SYS0F.SYS - FreHD Limited version (same source code)
* Overlays are pre-loaded into Pages RAM, not dynamically
  * Are preloaded into Paged RAM as part of SYS0 on Floppy80
  * Are loaded (on demand) into normal RAM, like a normal DOS

## Caveats

This is a work in progress not all features are implemented at this time.
See the separate Compatibility document for what is and isn't supported.

## Todo
* FIRMWARE - STAatus command display Paging Info 
* FIRMWARE - Create a loader for the Boot.SYS startup block into FDC boot
* FIRMWARE - create a floppy FDC loader for Boot.SYS at $4200

### Issues
* Basic Error messages don't appear to be displaying correctly.
* Booting on Pico Version detection flips from Non to PICO

### Improvment
* #xxxXXX (command name itself) internal commands should be case-insensitive.
* Improve the addition of .CMD to a filename when execuing from CMD processor.
* Overlay B for basic save load etc, should error out if can locate the command
* Command Processor (initial code) needs to me moved more into the overlay
* FreHD DIR should not display directories
* #DIR command on the PICO should support filtering

### PicoRAM
* Need to Sort out loader Issues 
* Need to build 2 sets of artifacts - 1 for Frehd overlays, and 1 for PicoRam
* Conditional Build directives #IFDEF FREHD_BUILD
* Remove the ENHANCED runtime variable directive

### High Priority
* DIR command should support parameters (PICO)
* Add a #CD command (PICO)
* Add a #LOAD (but not run) command

### DOS Entry Points
* InitFile / OpenFile
* CloseFile
* ReadFile / WriteFile
* Rewind / BackSpace / Skip / EOF

### Medium
* Add a #COPY command
* Add a #DEL KILL (basic) command
* Add a #MKDIR command
* Add a #REN command
* Add ability for search paths when looking for file.

### Low Priority
* Add a #HELP command
