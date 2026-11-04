
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
* Filename Extension addition 

### Improvement
* Loader should use FIRMWARE commands to enter LOADER mode, saving and restoring current Page
* Improve the code addition of .CMD to a filename when executing from CMD processor.
    * When using LOAD SAVE RUN "file/BAS:N" /BAS could be added if not specified
* running a program that has no END $ADDRESS - will run code based on last byte loaded - crash.
  * instead this should be detected and generate an error



