## Tools

## Building the Project

### General

The official Z80 Assembler used is [ZMAC](https://48k.ca/zmac.html)
 and `MAKE` is the build tool.

```
% zmac --version
zmac: https://48k.ca/zmac.html (validated with version 18oct2022).
```

### Visual Studio 2026 on Windows

Open kDOS.sln, then use Build Solution (Ctrl+Shift+B). The Makefile project
calls build.ps1, which runs zmac. Debug and Release produce the same Z80
binaries; x64 describes the Windows project configuration, not the target CPU.
F5 debugging of TRS-80 programs is not configured. The standard .z editor may
show plain text unless you install a suitable assembly-language extension.

Prerequisites
* Visual Studio 2026 with C++ project support (Desktop development with C++).
* Put zmac.exe in tools/zmac.exe (ignored by Git), or set ZMAC_EXE to its
  absolute path before starting Visual Studio. No assembler is redistributed.

PowerShell alternatives
.\build.ps1
.\build.ps1 -Action Rebuild
.\build.ps1 -Action Clean
.\build.ps1 -Assembler 'C:\path\to\zmac.exe'

Outputs: build/SD-CARD (14 binaries from 13 assembly targets, plus SYS/HARDWARE.cfg and SYS/settings.cfg).
Listings and intermediate files: build/src/zout.
Builds never copy to removable media or flash the Pico. Clean removes only generated assembly and SD-card outputs under build;
it preserves build/vs because Visual Studio may hold its logs open. tools/zmac.exe is preserved.
These outputs are compiled from current upstream plus this branch's changes;
they are not the earlier Beta1 test package. Keep a matching release backup
and check upstream firmware requirements before testing on physical hardware.

## Testing

Regression tests (optional; Python 3.10+)
python -m pip install -r tests/requirements.txt
python tests/test_console.py
See tests/README.txt for scope and hardware-validation limitations.

## Git workflow

For a pull request, create a fork of kiwisincebirth/TRS-80-KDOS on GitHub,
add that fork as a remote named fork, and push the contribution branch there.
Keep origin pointing at the author's repository to fetch future updates.
You can then open a pull request from your fork's branch to upstream main.
All upstream author credits remain in the sources.
