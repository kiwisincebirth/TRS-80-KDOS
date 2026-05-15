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
as they use standard DOS API calls. Programs that directly 
access FDC hardware or undocumented (non-standard) API calls will not function.

## Features

Core Features
* Modern Filesystem 
  * Files are stored natively on the FAT filesystem.
  * File directories are supported, (currently 1 directory at a time)
  * Automatic conversion of traditional filename/ext into filename.ext
* DOS Features
  * DOS commands are typed into the BASIC command shell
  * Most DOS entry points at $4400 are supported.
  * Interrupts with real Time Clock supported
* BASIC features
  * Extended Basic functions are supported
  * Disk File IO Statements are NOT supported
  * Long error messages ar displayed
* Has a Low memory overhead than a traditional DOS
  * Requires about 0.5Kb of main memory space.
  * 47800 Bytes Free, compared with 48350 on Level 2 
  * Memory from $4500 is available for application usage.

## Components

This solution requires:
* Model 1 computer with 16K (or 48k) RAM
* SD Card for file storage.
* Expansion Interface is NOT required

And if you need to build this project
* [ZMAC](https://48k.ca/zmac.html) is the assembler used
* `MAKE` is the preferred build tool

### Hardware

The Floppy 80 (model 1) is the primary hardware required by this solution. 
 
FreHD is supported in a basic very basic form mainly for emulation and testing purposes

## Provided

The solution provides Software that runs on TRS-80, provides DOS like features. 
The software is stored and loaded fom SD card 

An Pi Pico v2 (RP2350) firmware provides
* A command API similar to (but a superset of) FreHD, to provide needed File capabilities.
* 128KB Paged Memory (in the $3000 - $37DF memory region), for low DOS overhead
* Optional 32 Kb of High Memory, for use in 16KB machines
* A small Floppy Disk emulation to support the loading of a boot block at start

## Supported

|              | Floppy 80            | Caveat                     |      |
|--------------|----------------------|----------------------------|------|
| BASIC        | LOAD "filename.BAS"  | Load a basic Program       | All  |
| Commands     | SAVE "filename.BAS"  | Save a program to Disk     | All  |
|              | RUN "filename.BAS"   | Load and Run a program     | All  |
|              | KILL "filename"      | Delete a file (todo)       | Pico | 
|              | MERGE "filename"     | Merge a file (todo)        | Pico | 
|              | -                    |                            |      |
| BASIC        | &Hxx                 | Hexadecimal Constant       | Pico |
| Instructions | &Oxx                 | Octo-decimal Constant      | Pico |
|              | DEF FNn(A)=A         | Define a User Function     | Pico |
|              | DEF USRn=ADDR        | Define a Call address      | Pico |
|              | FNn(A)               | Invoke a User Function     | Pico |
|              | INSTR(X$,Y$)         | String Search function     | Pico |
|              | LINE INPUT A$        | Input an entire line       | Pico |
|              | MID(X$,N,N)=""       | Mid String Assignment      | Pico |
|              | TIME$                | RTC Current DateTime       | Pico |
|              | USRn(A)              | Invoke a Call address      | Pico |
|              |                      |                            |      |
| BASIC Errors | Display Full Error   |                            | Pico |
|              |                      |                            |      |
| DOS          | #filename            | Runs a CMD program         | All  |
|              | #CD {dirName}        | Set working directory      | Pico |
|              | #COPY {f1} {f2}      | Copy a File (todo)         | Pico |
|              | #DEL {filename}      | delete file or directory   | Pico |
|              | #DIR {wildcard}      | display directory contents | All  |
|              | #LOAD {filename.CMD} | Load a CMD program         | All  |
|              | #MKDIR {dirname}     | Make a directory           | Pico |
|              | #MOVE {f1} {f2}      | move file or directory     | Pico |
|              | #PWD                 | display current directory  | Pico |
|              | #REN {f1} {f2}       | rename file or directory   | Pico |

## Operation

### Startup

At startup holding the <CLEAR> key will :
* Disable Virtual RAM and instead use Liner Overlay RAM. 
* Reduce available ram by 512 bytes needed for overlay loading
* Disable Extended basic features, which require virtual memory.
* Disable any AUTO processing

### General Operation

Pressing enter will switch between DOS and BASIC prompts.

When entering filenames the preference is to use a modern format.
e.g. FILENAME.EXT , but the tradition format of FILENAME/EXT
is generally supported within constrains e.g. PATH/FILENAME/EXT
will be interpreted as PATH/FILENAME.EXT

## Caveats

### Work In Progress
This is a work in progress not all features are implemented at this time.
See the separate Compatibility document for what is and isn't supported.

### FreHD solution
When running this on a FreHD there are several limitations
* Only provides a small sub set of functions (frehd limited firmware)
* Consumes 512 bytes more RAM for overlays (no paged ram)
* file management, and sub-Directories are not supported
* Many DOS API's (support File IO) are not supported
* Doesn't support Disk Basic extensions.

## Future 

### Features

**Named Virtual Directories**

Defined as volume identifiers on existing File name e.g. :1 thru :9
When a file is specified with a Drive :1 - :9 then  virtual dive will be used
Static config can be used for defining these virtual . e.g. 

```
DIR1=namedDirectory1 ...
DIR9=namedDirectory9
```

**Search Path**

Several directories can be specified that allow a virtual search path
meaning if not fund on :0 will search other drives in order to find it.
very much like the dos PATH command. Used when opening a file for Read access 
e.g. 

```
PATH=/BIN;/SYS
```




