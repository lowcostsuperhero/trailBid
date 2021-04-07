all: trailBid.py

always.o:

generate.py: always.o
	python.exe generate.py iahLunar

trailBid.py: always.o
	python.exe trailBid.py iahLunar
