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
  * Between 0.75 and 1.25 Kb main memory space used.

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

|            | Floppy 80               | FreHD                       |
|------------|-------------------------|-----------------------------|
| ROM        | Requires a Standard ROM | Requires FreHD autoboot ROM |
| ROM        | Load Floppy Boot $4200  | Loads Boot Block to $5600   |
| Boot Block |                         | Loads custom /FreHd.ROM     |
| Boot Block | Loads /SYS/BOOT.CMD     | Loads /SYS/BOOT.CMD         |
| Boot.CMD   | Detects Hardware        | Detects Hardware            |
| Boot.CMD   | Loads /SYS/SYS0FLOP.SYS | Loads /SYS/SYS0FRED.SYS     |
| Overlays   | -included in SYS0-      | Loads /SYS/SYS(A-Z).SYS     |

* FreHD.ROM - is a simple loader just chains to BOOT.CMD 
* Boot.CMD has detection for the underlying hardware
* SYS0xxxx.SYS - is based off same source code but has different features
* Overlays are pre-loaded into Pages RAM, not dynamically
  * Are preloaded into Paged RAM as part of SYS0 on Floppy80
  * Are loaded (on demand) into normal RAM, like a normal DOS

## Caveats

This is a work in progress not all featurs are implemented at this time.
See the seperate Compatibility document for what is and isnt supported.

## Todo

### Issues
* DIR command on PicoRAM only displaying a single item

### Improvment
* #DIR and other internal commands should be case-insensitive.
* Improve the addition of .CMD to a filename when execuing from CMD processor.
* Command Processor (initial code) needs to me moved more into the overlay
* FreHD DIR should not display directories

### High Priority
* Sort out the FreHD and Pico Loaders, as per the design
  * Need to build 2 sets of artifacts - 1 for Frehd overlays, and 1 for PicoRam
  * Conditional Build directives #IFDEF FREHD_BUILD
  * Move the Overlays (Super Calls) into Pico RAM
* Implement a #LOAD <command.cmd> DOS command

### Medium
* Add a #LOAD (but not run) command
* Add a #CD command
* Add a #COPY command
* Add a #DEL KILL (basic) command
* Add a #MKDIR command
* Add a #REN command
* Add ability for search paths when looking for file.

### Low Priority
* Add a #HELP command
