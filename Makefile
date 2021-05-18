EVENTDIRECTORY = iahLunar

trailBid.py: always.o
	python.exe trailBid.py $(EVENTDIRECTORY)

always.o:

generate_dribble: rm_00-orderOfHashers
	python.exe generate.py $(EVENTDIRECTORY) dribble

generate_pool: rm_00-orderOfHashers
	python.exe generate.py $(EVENTDIRECTORY) pool

generate_random: rm_00-orderOfHashers
	python.exe generate.py $(EVENTDIRECTORY) random

rm_00-orderOfHashers: always.o
	rm -f $(EVENTDIRECTORY)/00-orderOfHashers.txt

clean: always.o
	rm -f $(EVENTDIRECTORY)/html/*.html
