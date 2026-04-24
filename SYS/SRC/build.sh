#!/bin/zsh
set -e

echo BUILD

echo Building Keyboard
./zmac keyboard.z --oo lst,cim,cmd,hex

echo Building BOOT
./zmac boot.z --oo lst,cim,cmd,hex

echo Building SYS0
./zmac sys0f.z --zmac --oo lst,cmd
./zmac sys0p.z --zmac --oo lst,cmd

echo Building OVERLAY\'s
./zmac overlayb.z --oo lst,cim
./zmac overlayc.z --oo lst,cim
./zmac overlayd.z --oo lst,cim
./zmac overlaye.z --oo lst,cim
./zmac overlayf.z --oo lst,cim
./zmac overlayg.z --oo lst,cim
./zmac overlayl.z --oo lst,cim
./zmac overlayo.z --oo lst,cim

echo DEPLOY
echo Copying Files to Parent

cp zout/boot.cmd     ../../frehd.rom
cp zout/boot.cim     ../BOOT.SYS
cp zout/sys0p.cmd    ../SYSP.sys
cp zout/sys0f.cmd    ../SYS0.sys
cp zout/overlayb.cim ../overlayb.sys
cp zout/overlayc.cim ../overlayc.sys
cp zout/overlayd.cim ../overlayd.sys
cp zout/overlaye.cim ../overlaye.sys
cp zout/overlayf.cim ../overlayf.sys
cp zout/overlayg.cim ../overlayg.sys
cp zout/overlayl.cim ../overlayl.sys
cp zout/overlayo.cim ../overlayo.sys

echo Copying Files to FreHD

cp zout/boot.cmd     ~/Documents/FreHD/frehd.rom
cp zout/boot.cim     ~/Documents/FreHD/SYS/BOOT.SYS
cp zout/sys0p.cmd    ~/Documents/FreHD/SYS/SYSP.sys
cp zout/sys0f.cmd    ~/Documents/FreHD/SYS/SYS0.sys
cp zout/overlayb.cim ~/Documents/FreHD/SYS/overlayb.sys
cp zout/overlayc.cim ~/Documents/FreHD/SYS/overlayc.sys
cp zout/overlayd.cim ~/Documents/FreHD/SYS/overlayd.sys
cp zout/overlaye.cim ~/Documents/FreHD/SYS/overlaye.sys
cp zout/overlayf.cim ~/Documents/FreHD/SYS/overlayf.sys
cp zout/overlayg.cim ~/Documents/FreHD/SYS/overlayg.sys
cp zout/overlayl.cim ~/Documents/FreHD/SYS/overlayl.sys
cp zout/overlayo.cim ~/Documents/FreHD/SYS/overlayo.sys

if mount | grep -q "/Volumes/FLOPPY90"; then

echo Copying Files to Floppy90

cp zout/boot.cmd     /Volumes/FLOPPY90/frehd.rom
cp zout/boot.cim     /Volumes/FLOPPY90/SYS/BOOT.SYS
cp zout/sys0p.cmd    /Volumes/FLOPPY90/SYS/SYSP.sys
cp zout/sys0f.cmd    /Volumes/FLOPPY90/SYS/SYS0.sys
cp zout/overlayb.cim /Volumes/FLOPPY90/SYS/overlayb.sys
cp zout/overlayc.cim /Volumes/FLOPPY90/SYS/overlayc.sys
cp zout/overlayd.cim /Volumes/FLOPPY90/SYS/overlayd.sys
cp zout/overlaye.cim /Volumes/FLOPPY90/SYS/overlaye.sys
cp zout/overlayf.cim /Volumes/FLOPPY90/SYS/overlayf.sys
cp zout/overlayg.cim /Volumes/FLOPPY90/SYS/overlayg.sys
cp zout/overlayl.cim /Volumes/FLOPPY90/SYS/overlayl.sys
cp zout/overlayo.cim /Volumes/FLOPPY90/SYS/overlayo.sys

fi

echo TRS80GP

open -a trs80gp --args -m1 \
  -frehd -frehd_dir ~/Documents/FreHD \
  -rom ~/GITHUB/TRS-80-ROMS/MDL1REV4.bin \



#  -b 441C -b 42e0 -b 4492 \
#  -b 443C -b 4428 -b 44420 \

#  -frehd_patch \
#  -b 4420 \
#  -b 4313 \
#  -i '#METEOR\r' \

#  -rom ~/GITHUB/TRS-80/MDL1REV3F.bin \
#  -i 'OPEN "OUTHOUS1.CMD"\r' \
#  -i '#DIR\r' \
