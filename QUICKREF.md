
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
"READY>" Prompt. Pressing "ENTER" (without typing a command) will switch to the 
DOS ":" prompt. To get a summary of DOS commands type the command "HELP"


## DOS input and directory paging

At a paused `DIR` listing, press **BREAK** to return to the DOS prompt while
keeping the displayed filenames. Any other key continues the listing. The
remaining Pico directory records are consumed silently before returning.

In normal paged-memory mode, the DOS `:` prompt remembers the last eight
submitted commands. **Up** recalls older commands and **Down** recalls newer
ones. Down past the newest restores the draft entered before browsing history.
Use **Left/Backspace** to delete from the end, type corrections, and press
**ENTER** to execute. **CLEAR** erases the current input; **BREAK** cancels it.
Empty ENTER still switches to BASIC. Empty and cancelled commands are not saved.

History accepts up to 127 characters per command and lasts until kDOS is
reloaded. It uses Pico pages 180-183 without reserving additional BASIC RAM.
Holding CLEAR at startup disables history along with the other paged features;
DIR cancellation still works. BASIC input and mid-line editing are unchanged.
