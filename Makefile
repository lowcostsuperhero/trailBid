all: trailBid.py

EVENTDIRECTORY = iahLunar

always.o:

generate.py: always.o
	rm -f $(EVENTDIRECTORY)/00-orderOfHashers.txt
	python.exe generate.py $(EVENTDIRECTORY) pool

generate_random: always.o
	rm -f $(EVENTDIRECTORY)/00-orderOfHashers.txt
	python.exe generate.py $(EVENTDIRECTORY) random

trailBid.py: always.o
	python.exe trailBid.py $(EVENTDIRECTORY)
