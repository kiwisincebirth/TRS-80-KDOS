
# DEV NOTES

## Tools

To Build this project
* [ZMAC](https://48k.ca/zmac.html) is the assembler used
* `MAKE` is the build tool

## Work In Progress (TODO)

### High Priority
* M1ZVM ZORK
* Debugger

### DOS Entry Points
Need to add these
* Date Time
  * (446D) @TIME todo Get the time "23:59:59" into (HL)
  * (4470) @DATE todo Get the date "12/12/99" into (HL)
* Filename Extension addition 

### Issues
* LOAD xxx.cmd from Emulator causes a FatFS Error 4
* typing LOAD "xx.bas" (basic command) from DOS causes a hang

### Improvement
* Loader code in Extra Ram move it to $4000
* Loader should use FIRMWARE commands to enter LOADER mode, saving and restoring current Page
* Improve the code addition of .CMD to a filename when executing from CMD processor.
    * When using LOAD SAVE RUN "file/BAS:N" /BAS could be added if not specified
* running a program that has no END $ADDRESS - will run code based on last byte loaded - crash.
  * instead this should be detected and generate an error

### Improvement - Error handling
* #RM BASIC - removing a directory (not empty) produced "FF Error 7" Access denied due to prohibited
  access or directory full -> Should provide better error.
* #MKdir BASIC - FF Error 8 - Exists
* Need "Access Denied" and "Exists" messages - but maybe
    * in RM we MAP the Access Denied to "Directory Not Empty"
    * in MKDIR we MAP the Exists     to "Directory Exists"

