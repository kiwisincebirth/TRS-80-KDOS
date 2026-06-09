# Future

## Reset

Reset Signal is not resetting the ROOT folder, left in sub folder.
* Ideally firmware should detect and handle reset
* Maybee add an API command (called at startup) to force a reset
* This could also close all the open files.

When Pressing RESET (NMI), ROM drops back to DOS Ready, rather than full reset
* Probably requires an updated ROM, since cold start immediately overwrites $4000 - $405D
* these addresses contain the clock and 402d dos reentry.
* Updated Rom could check for Flag and drop to 402D
* Boot-loader cold detect existing install, look for BYTE in (KBROWCLR EQU $41E5)
* Not load the full O/S - Paged Ram doesn't need to be touched.

Full reboot should not wipe out Clock, needs secondary storage.
* maybe just define an API on Pico (FREHD) to get time, and maintain it there
* existing SYS 0 static defines should be removed, setting during startup.

## Features

### Named Virtual Directories

Defined as volume identifiers on existing File name e.g. :1 thru :9
When a file is specified with a Drive :1 - :9 then  virtual dive will be used
Static config can be used for defining these virtual . e.g.

```
DIR1=namedDirectory1 ...
DIR9=namedDirectory9
```

### Search Path

Several directories can be specified that allow a virtual search path
meaning if not fund on :0 will search other drives in order to find it.
very much like the dos PATH command. Used when opening a file for Read access
e.g.

```
PATH=/BIN;/SYS
```

### Medium
* Add BASIC FILE IO statements
* Add a #COPY file.ext:N file.ext:N command
* Add a KILL basic statement, leveraging #DELETE
* Add a MERGE basic statement
* #DIR {optional: wildcard}{optional :dirNumber} - List contents of :0 or :1 - :9 -> rewrite


### Low Priority Commands
* #AUTO - startup command execution
* #APPEND - one file to another
* #REBOOT - jump to $0000
* #VER - something about the DOS build # Pico Build #
* #CLOSEALL - to close open file handles
* #TIME #DATE - allow the date and time to be displayed / set

## Configuration
* #SYSTEM - ND80 command to store configuration parameters
* #Status - display something about the Environment, implies some config to view/modify

### Todo
* FIRMWARE - STAatus command display Virtual Paging Info
* FIRMWARE - STAatus command display Heap size remaining

## Keyboard
Good Keyboard Driver e.g. LDOS, interrupt driven e.g. support typeahead
* support key repeat, using interrupts for timing?
* support flashing cursor
* keyboard @ key has the caps lock behaviour, it shoudn't.
* keyboard Shift @ key doesnt respont frequently, only every second keystroke.
