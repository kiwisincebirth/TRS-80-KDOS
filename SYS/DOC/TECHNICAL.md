
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

## Enhanced Filename & Path Handling

The DOS features a filename and path sanitiser that allows the TRS-80 to interact with a modern SD card.
This system supports both legacy TRS-DOS naming conventions and modern hierarchical FAT subdirectories.

### Core Features
* **Legacy Support:** Automatically translates the classic `FILENAME/EXT` syntax into modern `FILENAME.EXT` format.
* **Modern Pathing:** Supports standard FAT subdirectories (e.g., `GAMES/ACTION/ZAXON`).
* **Automatic Sanitization:** All filenames are automatically converted to uppercase and stripped of non-compatible characters.
* **Drive Mapping:** Use the `:D` suffix (0-9) to quickly access different "Mount Points" or directories configured on your SD card.
* **Password Stripping:** Automatically ignores the `.PASSWORD` suffix used in some legacy software, ensuring compatibility without manual file renaming.

### Some Examples

| Input Pattern       | Logic Applied        | Resulting Behavior                                          |
|:--------------------|:---------------------|:------------------------------------------------------------|
| `name.bas`          | **Case Insensitive** | File names are converted to uppercase e.g. `NAME.BAS`       |
| `NAME/BAS`          | **Legacy Ext**       | Single slash with 1-3 chars are converted `NAME.BAS`        |
| `/SYS/SYS0.SYS`     | **Absolute Path**    | Direct path from SD root.                                   |
| `../DIR/FILE.BAS`   | **Relative Path**    | Leading dots are preserved; slashes treated as directories. |
| `EDIT/ASM/CMD`      | **Hybrid File**      | Handles the Path and legacy extension `EDIT/ASM.CMD`        |
| `FILE.TXT:1`        | **Drive Map**        | `:1` is extracted as Drive ID 1 and removed from path.      |
| `F.PASS` (4+ chars) | **Password**         | Treated as legacy password; string is truncated.            |
| `F.PAS` (1-3 chars) | **Modern Ext**       | Treated as valid modern extension; extension is preserved.  |

### Filenames

The following inputs all result in the same FAT filename CONFIG.SYS:
* CONFIG.SYS (Modern FAT style)
* config.sys (User typing in lowercase)
* CONFIG/SYS (Legacy TRS-DOS style)
* CONFIG/SYS.PASSWORD (Legacy with password ignored)

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

## DOS Error Codes 

| Error Number | Error Message           | TRS-DOS |
|--------------|-------------------------|---------|
| 0            | No Error                | Yes     |
| 15           | Write Protected Disk    | Yes     |
| 16           | Illegal File Number     | Yes     |
| 19           | Illegal Filename        | Yes     |
| 24           | File Not Found          | Yes     |
| 28           | End of File Encountered | Yes     |
| 31           | Program Not Found       | Yes     |
| 32           | Illegal Drive Number    | Yes     |
| 34           | Load File Format Error  | Yes     |
| 58           | Denied, Not Empty       |         |
| 59           | File Exists             |         |
| 60           | Path Not Found          |         |
| 61           | Illegal DOS Function    |         |
| 62           | Internal DOS Error      |         |
| 63           | Unknown Error           |         |

## Hardware Address Map

The following is provided by the RP2350 Pico Hardware

| Address     |                                  |
|-------------|----------------------------------|
| 3000 - 3400 | Banked Memory Entry Points       |
| 3400 - 3600 | Banked Code Memory (swappable)   |
| 3600 - 37E0 | Banked Data Memory (swappable)   |
| 37E0        | Read and Reset RTC Interrupt     |
| 37EC        | FDC Command Status               |
| 37EF        | FDC Data Register                |
| 37F0        | Banked Code Memory Page Register |
| 37F1        | Banked Data Memory Page Register |
| IO Port $C2 | Pico DATA IO Port                |
| IO Port $C3 | Pico SIZE Register               |
| IO Port $C4 | Pico COMMAND Register            |
| IO Port $C5 | Pico ERROR Register              |
| IO Port $CF | Pico STATUS Register             |
