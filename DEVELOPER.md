
# DEV NOTES

## Tools

To Build this project
* [ZMAC](https://48k.ca/zmac.html) is the assembler used
* `MAKE` is the build tool

## Work In Progress (TODO)

### Todo
* FIRMWARE - STAatus command display Virtual Paging Info
* FIRMWARE - STAatus command display Heap size remaining
* FIRMWARE - Reset Signal is not resetting the ROOT folder, left in sub folder.

### Issues
* typing LOAD "xx.bas" (basic command) from DOS causes a hang
* running a program that has no END $ADDRESS - will run code based on last byte loaded - crash.
    * instead this should be detected and generate an error

### Keyboard
Good Keyboard Driver e.g. LDOS, interrupt driven e.g. support typeahead
* support key repeat, using interrupts for timing?
* support flashing cursor
* keyboard @ key has the caps lock behaviour, it shoudn't.
* keyboard Shift @ key doesnt respont frequently, only every second keystroke.

### Improvement
* Loader code in Extra Ram consider moving to $4000
* Improve the code addition of .CMD to a filename when executing from CMD processor.
    * When using LOAD SAVE RUN "file/BAS:N" /BAS could be added if not specified

### RTC
* Full reboot should not wipe out Clock, needs secondary storage.
    * maybe just define an API on Pico (FREHD) to get time, and maintain it there
    * existing SYS 0 static defines should be removed, setting during startup.

### Improvement - Error handling
* #RM BASIC - removing a directory (not empty) produced "FF Error 7" Access denied due to prohibited
  access or directory full -> Should provide better error.
* #MKdir BASIC - FF Error 8 - Exists
* Need "Access Denied" and "Exists" messages - but maybe
    * in RM we MAP the Access Denied to "Directory Not Empty"
    * in MKDIR we MAP the Exists     to "Directory Exists"

### High Priority
* M1ZVM
* Debugger

### DOS Entry Points
Need to add these
* Date Time
    * (446D) @TIME todo Get the time "23:59:59" into (HL)
    * (4470) @DATE todo Get the date "12/12/99" into (HL)
* Filename Extension

### Medium
* Add BASIC FILE IO statements
* Add a #COPY file.ext:N file.ext:N command
* Add a KILL basic statement, leveraging #DELETE
* Add a MERGE basic statement
* #DIR {optional: wildcard}{optional :dirNumber} - List contents of :0 or :1 - :9 -> rewrite

### Features
* Add ability for search paths when looking for file.
* Add ability for named directories :1 to :9
* NewDos 80 #System like command to store configuration parameters
* When Pressing RESET (NMI), ROM drops back to DOS Ready,
    * Probably requires an updated ROM, since cold start immediately overwrites $4000 - $405D
    * these addresses contain the clock and 402d dos reentry.
    * Updated Rom could check for Flag and drop to 402D
    * Boot-loader cold detect existing install, look for BYTE in (KBROWCLR EQU $41E5)
    * Not load the full O/S - Paged Ram doesn't need to be touched.
    *

### Low Priority Commands
* #AUTO - startup command execution
* #APPEND - one file to another
* #REBOOT
* #Status - display something about the Environment, implies some config to view/modify
* #VER - something about the DOS build # Pico Build #
* #CLOSEALL - to close open file handles
* #TIME #DATE - allow the date and time to be displayed / set
