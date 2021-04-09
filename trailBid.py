# name: $Id: trailBid.py 2 00:54:29 09-Apr-2021 rudyz $

import getopt
import posixpath
import sys

from resource import *
from setting  import *

from trail    import *
from timeSlot import *
from calendar import *
from hasher   import *
from bid      import *

###########################################################################
###########################################################################
###########################################################################
###
### T r a i l    B i d
###
###########################################################################
###########################################################################
###########################################################################

class TrailBid():
   """
   use: This is the highest level of organization for managing hashers and
        their bids to attend trail
   usage: Interpreted by Python; instantiated when __name__ is "__main__".
          Objects are not intended for interactive manipulation after
          construction, so no facility has been implemented to tear-down
          object ownership for re-reading data files or for re-executon of
          runBid() method
   imp: The set of trail bid data is stored in a series of CSV files in a
        subdirectory.
        The files, and fields, of the CSV files are:
           settings.txt : key = value file; not in CSV format
           timeSlots.txt: timeSlotId, sequence, trailGroupName
           trails.txt   : trailID, sequence, trailName, trailCapacity
           calendar.txt : timeSlotID, trailID
           hashers.txt  : hasherID, hasherName
           bids.txt     : hasherID, trailID, bidAmount
   """
   def __init__(self, eventDirectory = None):
      """
      usage: Optionally pass an event directory name in which all the
             needed data files are stored
      """
      printHeading("/// time slots ///", 0, 1)
      self.timeSlots = TimeSlots(eventDirectory)

      print()
      printHeading("/// trails ///", 0, 1)
      self.trails = Trails(eventDirectory)

      print()
      printHeading("/// calendar ///", 0, 1)
                                   # calendar is not a class. it joins trails
                                   # to timeSlots
      calendar(eventDirectory, self.timeSlots, self.trails)

      print()
      printHeading("/// hashers ///", 0, 1)
      self.hashers = Hashers(eventDirectory)

      bidsFilespec = os.path.join(eventDirectory, "bids.txt")
      if (os.path.isfile(bidsFilespec)):
         print()
         printHeading("/// bids ///", 0, 1)
         self.bids = Bids(bidsFilespec, self.hashers, self.trails)

###########################################################################

   def printRelations(self):
      """
      use: Print the constructed relations between the instantiated
           objects
      """
      if (settings["verbosity"] >= 2):
         print()
         printHeading("/// time slot trails ///", 0, 1)
         self.timeSlots.printTrails(indent = 0, headLevel = 2, detail = 2)

      if (settings["verbosity"] >= 3):
         print()
         printHeading("/// time slot bids ///", 0, 1)
         self.timeSlots.printBids(indent = 0, headLevel = 2, detail = 1)

      if (settings["verbosity"] >= 3):
         print()
         printHeading("/// time slot hashers ///", 0, 1)
         self.timeSlots.printHashers(indent = 0, headLevel = 2, detail = 1)

      if (settings["verbosity"] >= 3):
         print()
         printHeading("/// time slot unique hashers ///", 0, 1)
         for timeSlot in self.timeSlots:
            printHeading(str(timeSlot), indent = 0, headLevel = 2)
            timeSlot.getHashers().printHashers(
                                     indent = 1, headLevel = 3, detail = 1)

      if (settings["verbosity"] >= 3):
         print()
         printHeading("/// hasher bids ///", 0, 1)
         self.hashers.printBids(indent = 0)

###########################################################################

   def runBid(self):
      """
      use: Process bid data, awarding trails to hashers who have submitted
           bids to attend trails
      """
      printHeading("/// run bid ///", 0, 1)
      self.timeSlots.runBid()

###########################################################################

   def printResult(self, detail = 0):
      """
      use: Uninspired wrapper for printResultByTrail() followed by
           printResultByHasher()
      pre: runBid() processing must be completed
      """
      self.printResultByTrail(detail = detail)
      print()
      self.printResultByHasher(detail = detail)

###########################################################################

   def printResultByHasher(self, detail = 0):
      """
      use: For every hasher who has submiited one or more bids, print the
           hasher and trail information of the successful bids
      pre: runBid() processing must be completed
      """
      printHeading("/// results by hasher ///", 0, 1)
      self.hashers.printResultByHasher( # detail: 0=bare; 1=show bid value
                      indent = 0, headLevel = 2, detail = detail)

###########################################################################

   def printResultBySuccessfulHasher(self, detail = 0):
      """
      use: For every hasher with at least one successful bid, print the
           hasher and trail information of the successful bids
      pre: runBid() processing must be completed
      """
      printHeading("/// results by successful hasher ///", 0, 1)
      self.hashers.printResultBySuccessfulHasher(
                      indent = 0, headLevel = 2, detail = detail)

###########################################################################

   def printResultByUnsuccessfulHasher(self, detail = 0):
      """
      use: For every hasher who has submitted at least one bid but was
           unsuccessful on all submitted bids, print the hasher
      pre: runBid() processing must be completed
      """
      printHeading("/// results by unsuccessful hasher ///", 0, 1)
      self.hashers.printResultByUnsuccessfulHasher(
                      indent = 0, headLevel = 2, detail = detail)

###########################################################################

   def printResultByNoBidHasher(self, detail = 0):
      """
      use: For every hasher without any bids for any trails, print the
           hasher
      pre: runBid() processing must be completed
      """
      printHeading("/// hashers with no bids ///", 0, 1)
      self.hashers.printResultByNoBidHasher(
                      indent = 0, headLevel = 2, detail = detail)

###########################################################################

   def printResultByTrail(self, detail = 0):
      """
      use: For each time slot, print list of trails and the hashers with
           a successful bid for the trail
      pre: runBid() processing must be completed
      """
      printHeading("/// results by trail ///", 0, 1)
      self.timeSlots.printResultByTrail( # detail: 0=bare; 1=show bid value
                        indent = 0, headLevel = 2, detail = detail)

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
   eventDirectory = None
   verbosity      = 0
   opts, args     = getopt.getopt(sys.argv[1:], "vh")

   for opt in opts:
      pprint(opt)
      if (opt[0] == "-v"):
         verbosity += 1
      elif (opt[0] == "-h"):
         print("usage: " + selfName + "[options] directoryName")
         print("where options are:")
         print("   -v verbose; more v for more verbosity")
         print("   -h help")
         exit()

   for arg in args:
      if (eventDirectory is None):
         eventDirectory = arg
   if (eventDirectory is None):
      eventDirectory = "event"

   if (not os.path.isdir(eventDirectory)):
      sys.stderr.write(selfName + ": no event directory: " +
                       eventDirectory)
      exit(1)

   printHeading("/// settings ///", 0, 1)
   settings.readFile(eventDirectory)

   settings.setDefault("bidAllowance", 100)
   settings["verbosity"] = verbosity
   pprint(settings.dict)

###################################

   print()
   trailBid = TrailBid(eventDirectory)

   trailBid.printRelations()

   print()
   trailBid.runBid()

   if (settings["verbosity"] >= 1):
      print()
      printHeading("/// ranked bids ///", 0, 1)
      for timeSlot in trailBid.timeSlots:
         print(timeSlot.prettyListDisplay())
         timeSlot.getBids().sortEquitably().printBids(indent    = 0,
                                                      headLevel = 2,
                                                      detail    = 1)

   print()
#    trailBid.printResult(1)
   trailBid.printResultByTrail(detail = 0)
   print()
#    trailBid.printResultByHasher(detail = 0)
   trailBid.printResultBySuccessfulHasher(detail = 0)

   print()
   trailBid.printResultByUnsuccessfulHasher(detail = 0)

   print()
   trailBid.printResultByNoBidHasher(detail = 0)

###########################################################################
