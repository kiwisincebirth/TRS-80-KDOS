./zmac loader.z --oo lst,cim
./zmac frehd.z --oo lst,cmd
./zmac overlayb.z --oo lst,cim
./zmac overlayc.z --oo lst,cim
./zmac overlayd.z --oo lst,cim
./zmac overlaye.z --oo lst,cim
./zmac overlayf.z --oo lst,cim
./zmac overlayl.z --oo lst,cim

# zmac is required for local labels
./zmac BASIC.z --zmac --oo lst,cmd,hex

cp zout/frehd.cmd    ../../frehd.rom
cp zout/frehd.cmd    ../SYS0.sys
cp zout/loader.cim   ../LOADER.sys
cp zout/overlayb.cim ../overlayb.sys
cp zout/overlayc.cim ../overlayc.sys
cp zout/overlayd.cim ../overlayd.sys
cp zout/overlaye.cim ../overlaye.sys
cp zout/overlayf.cim ../overlayf.sys
cp zout/overlayl.cim ../overlayl.sys

cp zout/frehd.cmd    ~/Documents/FreHD/frehd.rom
cp zout/frehd.cmd    ~/Documents/FreHD/SYS/SYS0.sys
cp zout/loader.cim   ~/Documents/FreHD/SYS/LOADER.sys
cp zout/overlayb.cim ~/Documents/FreHD/SYS/overlayb.sys
cp zout/overlayc.cim ~/Documents/FreHD/SYS/overlayc.sys
cp zout/overlayd.cim ~/Documents/FreHD/SYS/overlayd.sys
cp zout/overlaye.cim ~/Documents/FreHD/SYS/overlaye.sys
cp zout/overlayf.cim ~/Documents/FreHD/SYS/overlayf.sys
cp zout/overlayl.cim ~/Documents/FreHD/SYS/overlayl.sys


open -a trs80gp --args -m1 -dx \
  -frehd_dir ~/Documents/FreHD \
  -rom ~/GITHUB/TRS-80-ROMS/MDL1REV4.bin \


#  -frehd -frehd_patch \
#  -b 4420 \
#  -b 4313 \
#  -i 'OPEN "METEOR.CMD"\r' \

#  -rom ~/GITHUB/TRS-80/MDL1REV3F.bin \
#  -i 'OPEN "OUTHOUS1.CMD"\r' \
#  -i '#DIR\r' \
# -b 4600 -b 024f
