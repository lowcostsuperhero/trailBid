# name: $Id: generate.py 3 16:16:37 06-Sep-2021 rudyz $
"""
use: Generate hashers.txt and bids.txt files located in the event
     directory. These generated hashers and their bids may be useful
     for development and/or debugging. Under normal circumstances, this
     generation would not be required since this data would be expected
     to be supplied from actual bidding
usage: For help:
          python generate.py -h
"""
import csv
import getopt
import os
import posixpath
import random
import secrets
import sys

from pprint import pprint

from setting import *

selfName = os.path.basename(sys.argv[0])

###########################################################################

def generateHashers(hashers, eventDirectory, mode):
   """
   use: Generate a number of virtual hashers
   usage: Pass:
             hashers       : number of virtual hashers to generate
             eventDirectory: directory name into which hashers.txt file
                             to be created
             mode          : mode opening file:
                                w: create file for writing
                                a: create file if needed, then open for
                                   append
   imp: Structure of hashers.txt CSV file:
           hasherID,sequence,hasherName
   """
   file = open(os.path.join(eventDirectory, "hashers.txt"), mode)
   file.write("hasherID,sequence,hasherName\n")
   for id in range(1, hashers + 1):
      file.write(f"{id}, {id}, Hasher {id:04d}")
   file.close()

###########################################################################

def generateBids_dribble(hashers, trailMin, trailMax, allowance,
                        eventDirectory, mode):
   """
   imp: Structure of bids.txt CSV file:
           hasherID,trailID,bidAmount
        The first hasher bids the maximum value on the zeroeth trail (T0).
        Each subsequent hasher transfer bid value from T0 to successive
        trails. The span of trails to be credited with additional bid
        values from T0 will range from T1 to TM, where M is the total
        number of trails in the timeslot; once the span has incremented
        to M, it will restart back from 1. For each iteration, for every
        trail N between [1, M] to be credited addtional bid values, all
        trails from [1..N] must also be credited with additional bid
        values transferred from T0
   """
   file = open(os.path.join(eventDirectory, "bids.txt"), mode)
   if (mode == "w"):
      file.write("hasherID,trailID,bidAmount\n")
   bids = {}
   for trailId in range(trailMin, trailMax + 1):
                                # initialize the bid template
      bids[trailId] = allowance if trailId == trailMin else 0

   span = 0
   for hasherId in range(1, hashers + 1):
      spanMin = trailMin
      for trailId in range(trailMin, trailMin + span + 1):
                                # shift this hasher's bids
         if (bids[spanMin] == 0):
            spanMin += 1
            trailId  = spanMin
         bids[spanMin] -= 1
         bids[trailId] += 1

      for trailId in range(trailMin, trailMax + 1):
         if (bids[trailId] != 0):
            file.write(f"{hasherId}, {trailId}, {bids[trailId]}\n")

         if trailId == trailMax:
                                # print out hasher's bid matrix
            output = f"hasherID:>5d"
            for outId in range(trailMin, trailMax + 1):
               output = f"{output} {bids[outId]:>4d}"
            print(output)

      span = (span + 1) % (trailMax - trailMin + 1)
   file.close()

###########################################################################

def generateBids_pool(hashers, trailMin, trailMax, allowance,
                      eventDirectory, mode):
   """
   imp: Structure of bids.txt CSV file:
           hasherID,trailID,bidAmount
        The first hasher bids the maximum value on the zeroeth trail (T0).
        Each subsequent hasher transfer bid value from T0 to successive
        trails. The span of trails to be credited with additional bid
        values where a bid value will transfer from TN to T(N+1) if the
        bid values will not result in a situation where the bid value of
        TN is less than T(N+1).
   """
   file = open(os.path.join(eventDirectory, "bids.txt"), mode)
   if (mode == "w"):
      file.write("hasherID,trailID,bidAmount\n")
   bids = {}
   for trailId in range(trailMin, trailMax + 1):
                                # initialize the bid template
      bids[trailId] = allowance if trailId == trailMin else 0

   for hasherId in range(1, hashers + 1):
      shifted = 0
      for trailId in range(trailMax, trailMin, -1):
                                # shift this hasher's bids
         if (bids[trailId - 1] > (bids[trailId]) ):
            bids[trailId - 1] -= 1
            bids[trailId    ] += 1
            shifted           += 1

      if (shifted == 0):
         for trailId in range(trailMin, trailMax + 1):
            bids[trailId] = allowance if trailId == trailMin else 0

      for trailId in range(trailMin, trailMax + 1):
         if (bids[trailId] != 0):
            file.write(f"{hasherId}, {trailId}, {bids[trailId]}\n")

                                # print out hasher's bid matrix
         if trailId == trailMax:
            output = f"{hasherID:>5d}"
            for outId in range(trailMin, trailMax + 1):
               output = f"{output} {bids[outID]:>4d}"
            print(output)

   file.close()

###########################################################################

def generateBids_random(hashers, trailMin, trailMax, allowance,
                        eventDirectory, mode):
   """
   imp: structure of bids.txt CSV file:
           hasherID,trailID,bidAmount
   """
   span = trailMax - trailMin

   file = open(os.path.join(eventDirectory, "bids.txt"), mode)
   if (mode == "w"):
      file.write("hasherID,trailID,bidAmount\n")

   for hasherId in range(1, hashers + 1): #
      bids   = {}
      trails = []
      for trailId in range(trailMin, trailMax + 1):
         bids[trailId] = 0
         trails.append(trailId)

      interested = secrets.randbelow(span + 1) + 1
      random.shuffle(trails)
      trails = trails[0:interested]

      reserve = span
      balance = allowance
      for trailId in trails:
         if trailId == trails[-1]:
            bidValue = balance
         else:
            bidValue = secrets.randbelow(balance - reserve) + 1
            balance -= bidValue
            reserve -= 1
         bids[trailId] = bidValue

      output = f"{hasherId:>5d}"
      for trailId in range(trailMin, trailMax + 1):
         if (bids[trailId] != 0):
            file.write(f"{hasherId}, {trailId}, {bids[trailId]}\n")
         output = f"{output} {bids[trailId]:>4d}"
      print(output)

   file.close()

###########################################################################
###########################################################################
###########################################################################
###
### m a i n
###
###########################################################################
###########################################################################
###########################################################################

if ( __name__ == "__main__" ):
   hashers        = 2000
   eventDirectory = None
   distribution   = None
   opts, args     = getopt.getopt(sys.argv[1:], "n:h")
   timeSlots      = {}

   for opt in opts:
      if (opt[0] == "-n"):
         hashers = int(opt[1])
      elif (opt[0] == "-h"):
         print(f"usage: {selfName} [options] [directoryName [distribution]]")
         print( "where option are:")
         print(f"   -nNumber number of hashers to generate; if not provided,"
                  f" defaults to {hashers}")
         print( "   -h       help")
         print( "If directory name is not provided, it defaults to 'event';")
         print( "directoryName for the generated datafiles must already exist,")
         print( "distribution is one of: dribble, pool, or random;")
         exit(0)

   for arg in args:
      if (eventDirectory is None):
         eventDirectory = arg
      elif (distribution is None):
         distribution   = arg
      else:
         sys.stderr.write(f"{selfName}: unwanted extra argument: {arg}\n" )
         exit(1)

   if (eventDirectory is None):
      eventDirectory = "event"
   if (distribution is None):
      distribution   = "random"

   if (not os.path.isdir(eventDirectory)):
      sys.stderr.write(f"{selfName}: directory does not exist: "
                       f"{eventDirectory}\n")
      exit(1)

   settings.readFile(eventDirectory)
   settings.setDefault("bidAllowance", 100)
   bidAllowance = int(settings["bidAllowance"])

   filespec = os.path.join(eventDirectory, "calendar.txt")
   with (open(filespec, "r")) as csvfile:
      csvReader = csv.reader(csvfile)
      if (csv.Sniffer().has_header(open(csvfile.name).read(1024))):
         next(csvReader)
      for row in csvReader:
         if (len(row) != 0):
            timeSlotId = int(row[0])
            trailId    = int(row[1])
            if (timeSlotId not in timeSlots):
               timeSlots[timeSlotId] = []
            timeSlots[timeSlotId].append(int(trailId))

   generateHashers(hashers, eventDirectory, "w")
   fileMode = "w"
   for timeSlotId in timeSlots:
      trailMin = min(timeSlots[timeSlotId])
      trailMax = max(timeSlots[timeSlotId])

      if (distribution == "dribble"):
         generateBids_dribble(hashers, trailMin, trailMax, bidAllowance,
                              eventDirectory, fileMode)
      elif (distribution == "pool"):
         generateBids_pool   (hashers, trailMin, trailMax, bidAllowance,
                              eventDirectory, fileMode)
      elif (distribution == "random"):
         generateBids_random (hashers, trailMin, trailMax, bidAllowance,
                              eventDirectory, fileMode)
      fileMode = "a"
