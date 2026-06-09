
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
