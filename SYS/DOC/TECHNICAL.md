
# kDOS - Technical Reference

THIS DOCUMENT IS INCOMPLETE

## System Files

| File                | Description                               | Type   | Source       |
|---------------------|-------------------------------------------|--------|--------------|
| FREHD.ROM           | Relocating Boot Loader (FreHd)            | CMD    | BOOT.z       |
| /SYS/BOOT.SYS       | Relocating Boot Loader (Floppy Disk)      | Binary | BOOT.z       |
| /SYS/HARDWARE.CFG   | Used by Pico Firmware to Configure itself | TXT    |              |
| /SYS/KEYBOARD.CMD   | Loads /SYS/SYSP.SYS                       | CMD    | KEYBOARD.z   |
| /SYS/OVERLAY{x}.SYS | Non Banked RAM Runtime Overlays           | Binary | OVERLAY{x}.z |
| /SYS/SYS0.SYS       | Non Banked RAM Kernal Only                | CMD    | SYS0F.z      |
| /SYS/SYSP.SYS       | Full Banked RAM System, incl all overlays | CMD    | SYS0P.z      |

* FreHD.ROM - is a direct copy of BOOT.SYS in CMD format
* BOOT.SYS - 256 byte binary image, with ORG = $6000
* SYS0.SYS - FreHD Limited version (same source code)
* SYSP.SYS - Enhanced PICO full DOS, using banked memory
* Overlays are pre-loaded into Pages RAM, not dynamically
  * Are preloaded into Paged RAM as part of SYSP on Floppy80
  * Are loaded (on demand) into normal RAM, like a normal DOS

## Boot Process

|            | Floppy 80 M1            | F80 & FHD              | FreHD                       |
|------------|-------------------------|------------------------|-----------------------------|
| ROM        | Uses a Standard L2 ROM  | ->                     | Requires FreHD Autoboot ROM |
| ROM        | Loads Floppy Boot Block | ->                     | Loads FreHD Boot Block      |
| ROM        | (BOOT.SYS loaded $4200) | BOOT.SYS loaded $5000  | FreHD boot loaded to $5000  |
| Boot Block |                         |                        | Loads FREHD.ROM             |
| Boot Block |                         |                        | -aka- BOOT/CMD to $5200     |
| Boot.SYS   | Relocates to $5200      | <-                     |                             |
| Boot.SYS   | Detects Hardware        | <-                     | Detects Hardware            |
| Boot.SYS   | Loads /SYS/SYSP.SYS     | <-                     | Loads /SYS/SYS0.SYS         |
| SYS0.SYS   | SYSP Starts at $5400    | <-                     | SYS0 Starts at $5400        |
| Overlays   | -included in SYSP-      | <-                     | Loads /SYS/SYS(A-Z).SYS     |

## DOS Memory Map

The high level Memory map

| Address     | Contents              | For FreHD            |
|-------------|-----------------------|----------------------|
| 3400 - 3600 | DOS Overlay Area      | Moved to 4500-4700   |
|             | Disk Basic Extensions | n/a                  |
|             | Other DOS extensions  | n/a                  |
| 3600 - 37E0 | DOS Working Data      | n/a                  |
| 4000 - 41E8 | As per Level 2 Basic  |                      |
| 41E8 - 42F0 | DOS Resident Code 1   |                      |
| 42F1 - 4311 | System FCB Buffer     |                      |
| 4312 - 4314 | Undefined             |                      |
| 4315 - 4317 | Basic Buffer Prefix   |                      |
| 4318 - 43FF | Command Line Buffer   |                      |
| 4400 - 4480 | DOS Entry Points      |                      |
| 4480 - 44D0 | DOS Resident Code 2   |                      |
|             |                       | 4500 - 4700 Overlays |
| 44D4        | BASIC Program Start   | Moved up to 4704     |

And some important DOS Vectors and values

| Address |        | Contents                   | Issues |
|---------|--------|----------------------------|--------|
| 400C    | RST28  | DOS Super Call Dispatcher  |        |
| 400F    | RST30  | DOS DEBUG entry point      | (todo) |
| 4012    | RST38  | DOS Interrupt Service      |        |
| 4033    |        | Char I/O for Disk Files    |        |
| 4040    |        | Interrupt Timer Tick Count |        |
| 4041    |        | Time Seconds (0-59)        |        |
| 4042    |        | Time Minutes (0-59)        |        |
| 4043    |        | Time Hours (0-23)          |        |
| 4044    |        | Date Year (0-99)           |        |
| 4045    |        | Date Day (1-31)            |        |
| 4046    |        | Date Month (1-12)          |        |

## DOS Entry Points

| Address |        | Contents                   | Issues          |
|---------|--------|----------------------------|-----------------|
| 402D    | @EXIT  | No Error DOS Exit          | (Same as 4400)  |
| 4030    | @ABORT | DOS Error Exit             |                 |
| 4400    | @CMD   | No Error DOS Exit          |                 |
| 4405    | @CMNDI | Execute CMD and Exit       |                 |
| 4409    | @ERROR | Exit and Display Error     |                 |
| 440D    | @DEBUG | Debug Mode                 | Not Implemented |
| 4410    | @ADTSK | Add Interrupt Task         | Not Implemented |
| 4413    | @RMTSK | Remove Interrupt Task      | Not Implemented |
| 441C    | @FSPEC | Extract File Spec          |                 |
| 4420    | @INIT  | Create or Open File        |                 |
| 4424    | @OPEN  | Open Existing File         |                 |
| 4428    | @CLOSE | Close a File               |                 |
| 442C    | @KILL  | Delete an Open File        |                 |
| 4430    | @LOAD  | Load Program               |                 |
| 4433    | @RUN   | Load and Run Program       |                 |
| 4436    | @READ  | Read from Disk File        |                 |
| 4439    | @WRITE | Write to Disk File         |                 |
| 443C    | @VER   | Write and Verify           | (Same as 4339)  |
| 443F    | @REW   | Position File to Start     |                 |
| 4442    | @POSN  | Position File              |                 |
| 4445    | @BKSP  | Backspace Fle 1 Record     |                 |
| 4448    | @PEOF  | Position File to EOF       |                 |
| 4467    | @DSPLY | Display a String           |                 |
| 446A    | @PRINT | Print a String             |                 |
| 446D    | @TIME  | Time into (HL) buffer      |                 |
| 4470    | @DATE  | Date into (HL) buffer      |                 |
| 4473    | @FEXT  | Default Filename extension |                 |

ALSO
* (4427) * ND8Ø $82 identifying ND(8)0v(2) ???                                       
* (442B) * ND8Ø $Ø1 if Model I and $Ø3 if Model III.

### @CMNDI (4405) - Execute Command

Machine-code callers can use `CALL $4405` (`@CMNDI`) with HL pointing to
writable CR- or NUL-terminated command text. The command processor executes
an internal command and returns A=0/Z on success, or A=DOS error/NZ on failure.
BC, DE and HL may change. The paged implementation restores the caller's
code bank; the caller's data bank and DOS prompt mode are preserved.
Nested calls are rejected with Internal DOS Error. External program names
are excluded; internal LOAD is supported without executing the loaded code.
This returning behavior is a kDOS extension: historical TRSDOS, LDOS and
NewDOS versions use $4405 as a terminating command entry. Compatibility and
a broader command-return redesign are deferred for separate review.

BASIC CMD uses this interface; CMD uses code page 179 and data
page 41 only for a private command-string copy.

### @TIME (446D) Copy Time into (HL) buffer

Writes the time as HH:MM:SS eight characters at Register Pair HL. 
Each of the three values (00-99, binary) is turned into two decimal digits. 
Register Pair HL returns just past the text.
This API write exactly eight characters and do not append a terminator

### @DATE (4470) Copy Date into (HL) buffer

Writes the date as MM/DD/YY, eight characters at Register Pair HL. 
Each of the three values (00-99, binary) is turned into two decimal digits. 
Register Pair HL returns just past the text.
This API write exactly eight characters and do not append a terminator

## File IO

### Sequential character I/O

ROM `_GET` ($0013) and `_PUT` ($001B) dispatch file FCBs through $4033.
Supply DE=FCB and A=byte for PUT. GET returns A=byte; both return Z on
success or NZ with a DOS error in A (including 28 at EOF). The ROM preserves
BC, DE, HL and IX. Device DCBs continue through the existing ROM handlers.
The paged enhanced DOS driver in OVERLAYI currently requires LRL=1 and uses the
buffer pointer recorded by @OPEN/@INIT. Other record lengths and control
operations return Illegal DOS function; buffered byte access is future work.

BASIC input opens through @OPEN and closes through @CLOSE. Output uses
the additional OVERLAYF S_CREATEFILE service (same B/DE/HL contract as
@INIT) with create/truncate semantics. @INIT retains its existing
open-or-create behavior. No BASIC handler directly accesses Pico file ports.

### Basic FILE I/O

BASIC uses the shared DOS byte driver through ROM `_GET` and `_PUT`
(vector `$4033`), with one-byte records for exact lengths and EOF handling.
Large transfers may be slow. Append, random-access
records (`FIELD`, `GET`, `PUT`, etc.), `PRINT# USING`, `TAB` and `SPC` in
`PRINT#` are not included yet. These new commands target Floppy80's enhanced
file API; they do not add FreHD support. The DOS byte driver also accepts
machine-code callers with their own FCB and buffer; currently it requires
LRL=1. Buffered byte access for other record lengths is future work.



### Detection of /USR secondary directory during Open

#### Discussion 

Calling API Open, when loading an DOS Overlay
ld c,FA_OPEN_EXIST|FA_READ

loading a BASIC program
ld c,FA_OPEN_EXIST|FA_READ

Saving a BASIC Program
ld c,FA_CREATE_ALWAYS|FA_WRITE

Loading a User Binary File CMD into RAM
ld c,FA_OPEN_EXIST|FA_READ

Default to Open Existing file @OPEN
ld a,FA_OPEN_EXIST|FA_RW ; 

Open Existing or Create a new @INIT
ld a,FA_OPEN_ALWAYS|FA_RW ; 

Should perform secondary /USR lookup
* Loading a User Binary File CMD into RAM => ld c,FA_OPEN_EXIST|FA_READ
* @OPEN DOS Application API - Typically used for Loading => ld a,FA_OPEN_EXIST|FA_RW 

Will be Excluded because filename will ALWAYS contain explicit SLASH
* Calling API Open, when loading an /SYS/Overlay.SYS file => ld c,FA_OPEN_EXIST|FA_READ () -

NO Secondary ( /USR) should be appended
* loading a BASIC program => ld c,FA_OPEN_EXIST|FA_READ
* Saving a BASIC Program => ld c,FA_CREATE_ALWAYS|FA_WRITE
* @INIT DOS Application API - Typically used for Saving => ld a,FA_OPEN_ALWAYS|FA_RW

So the division is not clear easily definable the Code at a minimum 
should check for FA_OPEN_EXIST - before applying the Secondary /USR path. 
This only leaves the Loading a Basic Program which will find it in secondary. 
which is a bit of an edge case
* LOAD "PROG.BAS" - loads from /USR
* SAVE "PROG.BAS" will save in current directory

Its an edge case, but acceptable. But think code needs updating for FA_OPEN_EXIST.
