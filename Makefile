all: trailBid.py

always.o:

generate.py: always.o
	python.exe generate.py iahLunar pool

generate_random: always.o
	python.exe generate.py iahLunar random

trailBid.py: always.o
	python.exe trailBid.py iahLunar
