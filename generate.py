# name: $Id: generate.py 1 00:55:26 09-Apr-2021 rudyz $

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
   file.write("hasherID,hasherName\n")
   for id in range(1, hashers + 1):
      file.write(str(id) + ", " +
                 str(id) +
                 ", Hasher {:04d}".format(id) + "\n")
   file.close()

###########################################################################

def generateBids_dribble(hashers, trailMin, trailMax, allowance,
                        eventDirectory, mode):
   """
   imp: structure of bids.txt CSV file:
           hasherID,trailID,bidAmount
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
            file.write(str(hasherId)      + ", " +
                       str(trailId )      + ", " +
                       str(bids[trailId]) + "\n")

         if trailId == trailMax:
                                # print out hasher's bid matrix
            output = "{:>5d}: ".format(hasherId)
            for outId in range(trailMin, trailMax + 1):
               output = "{} {:>4d}".format(output, bids[outId])
            print(output)

      span = (span + 1) % (trailMax - trailMin + 1)
   file.close()

###########################################################################

def generateBids_pool(hashers, trailMin, trailMax, allowance,
                      eventDirectory, mode):
   """
   imp: structure of bids.txt CSV file:
           hasherID,trailID,bidAmount
   """
   file = open(os.path.join(eventDirectory, "bids.txt"), mode)
   if (mode == "w"):
      file.write("hasherID,trailID,bidAmount\n")
   bids = {}
   for trailId in range(trailMin, trailMax + 1):
                                # initialize the bid template
      bids[trailId] = allowance if trailId == trailMin else 0

   for hasherId in range(1, hashers + 1):
      for trailId in range(trailMin, trailMax):
                                # shift this hasher's bids
         if (bids[trailId] >= bids[trailId + 1] + 2):
            bids[trailId    ] -= 1
            bids[trailId + 1] += 1

      for trailId in range(trailMin, trailMax + 1):
         if (bids[trailId] != 0):
            file.write(str(hasherId)      + ", " +
                       str(trailId )      + ", " +
                       str(bids[trailId]) + "\n")

                                # print out hasher's bid matrix
         if trailId == trailMax:
            output = "{:>5d}: ".format(hasherId)
            for outId in range(trailMin, trailMax + 1):
               output = "{} {:>4d}".format(output, bids[outId])
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

      output = "{:>5d}: ".format(hasherId)
      for trailId in range(trailMin, trailMax + 1):
         if (bids[trailId] != 0):
            file.write(str(hasherId)      + ", " +
                       str(trailId )      + ", " +
                       str(bids[trailId]) + "\n")
         output = "{} {:>4d}".format(output, bids[trailId])
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
         print("usage: " + selfName + "[options]" +
                         " [directoryName [distribution]]")
         print("where option are:")
         print("   -nNumber number of hashers to generate; if not provided," +
                           " defaults to 2000")
         print("   -h       help")
         print("If directory name is not provided, it defaults to 'event';")
         print("directoryName for the generated datafiles must already exist,")
         print("distribution is one of: dribble, pool, or random;")

   for arg in args:
      if (eventDirectory is None):
         eventDirectory = arg
      elif (distribution is None):
         distribution   = arg
      else:
         sys.stderr.write(selfName + ": unwanted extra argument: " + arg)
         exit(1)

   if (eventDirectory is None):
      eventDirectory = "event"
   if (distribution is None):
      distribution   = "random"

   if (not os.path.isdir(eventDirectory)):
      sys.stderr.write(selfName + ": directory does no exist: " +
                                  eventDirectory)
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
