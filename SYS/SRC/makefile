.PHONY: build all

zmacbin=./zmac --zmac --oo lst,cim
zmacall=./zmac --zmac --oo lst,cim,cmd
zmaccmd=./zmac --zmac --oo lst,cmd

all: clean build deploy
build: boot sys0 overlays extras

boot:
	@echo "Building BOOT"
	@${zmacall} boot.z

sys0:
	@echo "Building SYS0"
	@${zmaccmd} sys0f.z
	@${zmaccmd} sys0p.z

overlays:
	@echo "Building Overlays"
	@${zmacbin} overlayb.z
	@${zmacbin} overlayc.z
	@${zmacbin} overlayd.z
	@${zmacbin} overlaye.z
	@${zmacbin} overlayf.z
	@${zmacbin} overlayg.z
	@${zmacbin} overlayh.z
	@${zmacbin} overlayh.z
	@${zmacbin} overlayl.z
	@${zmacbin} overlayo.z

extras:
	@${zmaccmd} keyboard.z

deploy:
	@echo "Deploying"
	@cp zout/boot.cmd     ../../frehd.rom
	@cp zout/boot.cim     ../BOOT.SYS
	@cp zout/sys0p.cmd    ../SYSP.sys
	@cp zout/sys0f.cmd    ../SYS0.sys
	@cp zout/overlayb.cim ../overlayb.sys
	@cp zout/overlayc.cim ../overlayc.sys
	@cp zout/overlayd.cim ../overlayd.sys
	@cp zout/overlaye.cim ../overlaye.sys
	@cp zout/overlayf.cim ../overlayf.sys
	@cp zout/overlayg.cim ../overlayg.sys
	@cp zout/overlayh.cim ../overlayh.sys
	@cp zout/overlayl.cim ../overlayl.sys
	@cp zout/overlayo.cim ../overlayo.sys
	@cp zout/keyboard.cmd ../KEYBOARD.CMD

clean:
	@rm -r -f zout/*.* zout
	@rm -r -f ../*.sys ../*.cmd ../*.SYS ../*.CMD
