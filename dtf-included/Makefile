setup:
	mkdir -p src/
	mkdir -p out/

abe: setup
	git clone https://github.com/nelenkov/android-backup-extractor.git src/abe
	cd src/abe; \
	  wget https://www.bouncycastle.org/download/bcprov-jdk15on-158.jar -O lib/bcprov-jdk15on-158.jar; \
	  ./gradlew build shadowJar; \
	  cp ./build/libs/abe-all.jar ../../out/abe.jar

apktool: setup
	git clone git://github.com/iBotPeaches/Apktool.git src/apktool
	cd src/apktool; \
	  ./gradlew build shadowJar; \
	  cp ./brut.apktool/apktool-cli/build/libs/apktool-cli-all.jar ../../out/apktool.jar; \
	  cp ./brut.apktool/apktool-lib/src/main/resources/prebuilt/linux/aapt ../../out/aapt

axmlprinter: setup
	git clone https://github.com/rednaga/axmlprinter src/axmlprinter2
	cd src/axmlprinter2; \
	  ./gradlew jar; \
	  cp ./build/libs/axmlprinter*.jar ../../out/axmlprinter2.jar

smali: setup
	git clone https://github.com/JesusFreke/smali.git src/smali
	cd src/smali; \
	  ./gradlew build; \
	  cp ./smali/build/libs/smali.jar ../../out/smali.jar; \
	  cp ./baksmali/build/libs/baksmali.jar ../../out/baksmali.jar

version:
	echo $(shell date +%Y-%m-%d) > out/VERSION

tar: version
	cd out; \
	  tar -cf ../build/included.tar ./*

fatTar: abe apktool axmlprinter smali tar

clean:
	rm -rf src/
	rm -rf out/
	rm -rf build/*
