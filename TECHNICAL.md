
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

* BOOT.SYS - 256 byte binary image, with ORG = $6000
* FreHD.ROM - is a direct copy of BOOT.SYS in CMD format
* SYSP.SYS - Enhanced PICO full DOS, using virtual memory
* SYS0.SYS - FreHD Limited version (same source code)
* Overlays are pre-loaded into Pages RAM, not dynamically
    * Are preloaded into Paged RAM as part of SYSP on Floppy80
    * Are loaded (on demand) into normal RAM, like a normal DOS

## DOS Memory Map

The high level Memory map

| Address     | Contents               | For FreHD            |
|-------------|------------------------|----------------------|
| 3400 - 3600 | DOS Overlay Area       | Moved to 4500-4700   |
| 3600 - 37E0 | DOS Loader Utility     | In Overlay Code      |
|             | RTC Clock Interrupt    | Not Supported        |
| 4000 - 41E8 | As per Level 2 Basic   |                      |
| 41E8 - 42E8 | String CMD Line Buffer |                      |
| 42E0 - 43E0 | DOS Resident Code 1    |                      |
| 43E0 - 4400 | System FCB Buffer      |                      |
| 4400 - 4480 | DOS Entry Points       |                      |
| 4480 - 44D0 | DOS Resident Code 2    |                      |
|             |                        | 4500 - 4700 Overlays |
| 44D0        | BASIC Program Start    | 4700 - Basic Program |

DOS Entry Points (4400-4480)

| Address |        | Contents                   | Issues          |
|---------|--------|----------------------------|-----------------|
| 402D    |        | No Error DOS Exit (44400)  |                 |
| 4400    | @CMD   | No Error DOS Exit          |                 |
| 4405    | @CMNDI | Execute CMD and Exit       | (Same as 4400)  |
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
| 446D    | @TIME  | Time into (HL) buffer      | todo            |
| 4470    | @DATE  | Date into (HL) buffer      | todo            |
| 4473    | @FEXT  | Default Filename extension |                 |

; todo should we insert these int table below
; (400C) RST 28H DOS Supervisor Call Dispatcher     
; (400F) RST 30h (DOS DEBUG entry point) Vector.
; (4012) RST 38h (Interrupt Service) Vector.                                                                                                 
; (4033) DOS Char I/O Driver for Disk Files
; (4427) * ND8Ø $82 identifying ND(8)0v(2)                                        
; (442B) * ND8Ø $Ø1 if Model I and $Ø3 if Model III.

## Hardware Address Map

The following is provided by the RP2350 Pico Hardware

| Address     |                                 |
|-------------|---------------------------------|
| 3000 - 3400 | Virtual Memory (page entry)     |
| 3400 - 3600 | Virtual Memory (page swappable) |
| 3600 - 37E0 | Scratch Memory (static)         |
| 37E0        | Read and Reset RTC Interrupt    |
| 37EC        | FDC Command Status              |
| 37EF        | FDC Data Register               |
| 37F0        | Virtual Memory Page Register    |
| IO Port $C2 | Pico DATA IO Port               |
| IO Port $C3 | Pico SIZE Register              |
| IO Port $C4 | Pico COMMAND Register           |
| IO Port $C5 | Pico ERROR Register             |
| IO Port $CF | Pico STATUS Register            |

