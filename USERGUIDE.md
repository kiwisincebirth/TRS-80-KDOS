# User Guide

## Startup

At startup holding the `CLEAR` key will :
* Disable Virtual RAM and instead use Liner Overlay RAM.
* Reduce available ram by 512 bytes needed for overlay loading
* Disable Extended basic features, which require virtual memory.
* Disable any AUTO processing

The `BREAK` key will disable loading entirely, like a Floppy disk
boot disable in a traditional setup.

## General Operation

The system will startup as a normal Level 2 basic system. You can type in a basic program
as you would normally on a non-disk system.

```shell
READY
>_
```

Pressing `ENTER` (without typing a command) will switch between DOS and BASIC prompts.
The `:` prompt is the equivalent of the DOS prompt, where disk commands are entered.

```shell
:_
```

## DOS Commands

Below is a summary of the suppoerted DOS commands. Noting if running on a FreHD
or under the FreHD TRS80GP emulation only the "FreHD" marked features are supported

| Command         | Description                   |       |
|-----------------|-------------------------------|-------|
| {filename}      | Runs a CMD program            | FreHD |
| CD {dirName}    | Set working directory         |       |
| COPY {f1} {f2}  | Copy a File (todo)            |       |
| DEL {filename}  | delete file or directory      |       |
| DIR {wildcard}  | display directory contents    | FreHD |
| DI              | Disable Interrupts / RTC      | FreHD |
| EI              | Enable Interrupts / RTC       | FreHD |
| HELP            | Display a summary of commands | FreHD |
| LOAD {filename} | Load a CMD program            | FreHD |
| MKDIR {dirname} | Make a directory              |       |
| MOVE {f1} {f2}  | move file or directory        |       |
| PWD             | display current directory     |       |
| REN {f1} {f2}   | rename file or directory      |       |

## BASIC Extensions

As well as the DOS commands, BASIC itself has been upgraded with
the non-disk I/O statements and extensions. The following are supported

|            | Command             | Description            |       |
|------------|---------------------|------------------------|-------|
| Commands   | LOAD "filename.BAS" | Load a basic Program   | FreHD |
|            | SAVE "filename.BAS" | Save a program to Disk | FreHD |
|            | RUN "filename.BAS"  | Load and Run a program | FreHD |
|            | KILL "filename"     | Delete a file (todo)   | FreHD | 
|            | MERGE "filename"    | Merge a file (todo)    | FreHD | 
|            | -                   | -                      |       |
| Statements | &Hxx                | Hexadecimal Constant   |       |
|            | &Oxx                | Octo-decimal Constant  |       |
|            | CVI CVS CVD         | Convert from String    |       |
|            | DEF FNn(A)=A        | Define a User Function |       |
|            | DEF USRn=ADDR       | Define a Call address  |       |
|            | FNn(A)              | Invoke a User Function |       |
|            | INSTR(X$,Y$)        | String Search function |       |
|            | LINE INPUT A$       | Input an entire line   |       |
|            | MID(X$,N,N)=""      | Mid String Assignment  |       |
|            | MKI$ MKS$ MKD$      | Convert to String      |       |
|            | TIME$               | RTC Current DateTime   |       |
|            | USRn(A)             | Invoke a Call address  |       |

As well as this BASIC will display the descriptive error messages.
Disk Basic I/O function are a future feature

## Filenames

Files names (including directories) should follow the 8.3 naming convention.
Longer file names will be truncated to 8.3 format. While this is supported
it is not recommended as the '~' character is not consistently displayed
or available on the standard keyboard.

When entering filenames the preference is to use a modern format.
e.g. FILENAME.EXT , but the tradition format of FILENAME/EXT
is generally supported within constrains e.g. PATH/FILENAME/EXT
will be interpreted as PATH/FILENAME.EXT
