# name: $Id: hasher.py 1 23:59:56 06-Apr-2021 rudyz $

import csv
import random
import sys

from setting import *

import bid   as bid_module
import trail as trail_module

from resource import *
from setting  import *

###########################################################################
###########################################################################
###########################################################################
###
### h a s h e r
###
###########################################################################
###########################################################################
###########################################################################

class Hasher:
   """
   use: A wanker who can bid on trails
   imp: Native attributes:
           id             : a unique internal identifier
           sequence       : default sorting order
           name           : name of hasher
        Virtual attributes:
           bids           : bids submitted by hasher
           successfulBids : hasher's successful bids
           order          : sorting order after sortByRandom()
           rank           : sorting order for Bids.sortEquitably(). This
                            rank is based on the product of sequence and
                            order
   """
   def __init__(self, id, sequence, name):
      self.id             = int(id)
      self.sequence       = int(sequence)
      self.name           = name.strip()
     ###
      self.bids           = bid_module.Bids() # bids submitted by this hasher
      self.successfulBids = bid_module.Bids() # successful bids to go on trail
      self.order          = self.sequence
      self.rank           = self.order

###################################

   def __str__(self):
      return(str(self.id) + ': ' + self.name)

###########################################################################

   @property
   def bidCount(self):
      """
      use: Number of bids submitted by hasher
      """
      return(self.bids.count)

###################################

   @property
   def bidValue(self):
      """
      use: Sum of values for all bids submitted by hasher
      """
      return(self.bids.value)

###################################

   @property
   def successfulBidCount(self):
      """
      use: Number of bids submitted by hasher that were successful
      """
      return(self.successfulBids.count)

###########################################################################

   def addBid(self, bid):
      """
      use: Add a bid to the list of bids submitted by hasher
      imp: If the new bid value causes the sum of bid values for the time
           slot to exceed the bidAllowance, a warning message will be
           printed but otherwise nothing adverse will occur
      """
      if (bid not in self.bids.list):
         oldBidValue = self.bids.valueByTimeSlotId(bid.timeSlot.id)
         self.bids.add(bid)
         newBidValue  = self.bids.valueByTimeSlotId(bid.timeSlot.id)
         bidAllowance = int(settings["bidAllowance"])
         if ((oldBidValue <= bidAllowance) and
             (newBidValue  > bidAllowance)):
            print("*** " + str(self) + ": exceeded bid allowance")
      else:
         raise DuplicateError("duplicate bid for trail " +
                              str(trail) + " by hasher " +
                              str(hasher))

###########################################################################

   def addSuccessfulBid(self, bid):
      """
      use: Usually called by runBid() method to add a winning bid to the
           hasher's list of winning bids
      """
      self.successfulBids.add(bid)

###########################################################################

   def isAttendingTimeSlot(self, timeSlotId):
      """
      use: Predicate indicating if hasher has a winning bid for a trail
           belonging to the time slot corresponding to the passed
           timeSlotId, presumably implying the hasher will be attending a
           trail within the time slot
      post: Return value is a boolean
      """
      return(self.successfulBids.getTrailsByTimeSlotId(timeSlotId).count != 0)

###########################################################################

   def prettyListDisplay(self):
      """
      use: A prettily formatted ID and name suitable for display in a list
           of hashers
      """
      return("{:<22s}".format("{:>5d}: {}".format(self.id, self.name)))
#       return("{:<35s}".format("{:>4d}/{:>4d}@{:>10d}${:d}%{:d}".format(
#                                  self.id,
#                                  self.order,
#                                  self.rank,
#                                  self.successfulBidCount,
#                                  self.bidCount) + ": " +
#                               self.name))

###########################################################################

   def printBids(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: Print all bids submitted by hasher
      usage: See TimeSlots.printBids()
      """
      print("".ljust(max(indent, 0)) + self.prettyListDisplay())
      for timeSlot in self.bids.getTimeSlots().sortBySequence():
         bids = self.bids.getBidsByTimeSlotId(timeSlot.id)
         bids.printTrails(indent    + 7 if indent >= 0 else indent   ,
                          headLevel + 1 if headLevel   else headLevel,
                          detail)

###########################################################################

   def printHasher(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: Print hasher's ID and name
      usage: See TimeSlots.printBids()
      """
      print("".ljust(max(indent, 0)) + self.prettyListDisplay())

###########################################################################

   def printResultByHasher(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: Print successful bids submitted by hasher
      usage: See TimeSlots.printBids()
      """
      self.printHasher(indent, headLevel, detail)
      self.successfulBids.printTrails(
                             indent    + 9 if indent >= 0 else indent   ,
                             headLevel + 1 if headLevel   else headLevel,
                             detail)

###########################################################################
###########################################################################
###########################################################################
###
### h a s h e r s
###
###########################################################################
###########################################################################
###########################################################################

class Hashers:
   def __init__(self, filespec = None):
      self.list      = []
      self.lookupIDs = {}

      if (filespec is not None):
         if (os.path.isdir(filespec)):
            filespec = os.path.join(filespec, "hashers.txt")

         with open(filespec, "r") as csvfile:
            lineNumber = 0
            csvReader  = csv.reader(csvfile)
            if (csv.Sniffer().has_header(open(csvfile.name).read(1024))):
               lineNumber += 1
               next(csvReader)
            for row in csv.reader(csvfile):
               lineNumber += 1
               if (len(row) != 0):
                  try:
                     hasher = Hasher(int(row[0]), row[1], row[2])
                     self.add(hasher)
                     if (settings["verbosity"] >= 2):
                        print(str(hasher))
                  except DuplicateError as exception:
                     if isinstance(exception, DuplicateError):
                        exception = "duplicate hasher ID"
                     writeFileReadError(filespec, lineNumber, exception,
                                        row[0] + ", " + row[1])
                     printFileReadError(lineNumber, row[0] + ", " + row[1])

            if (settings["verbosity"] < 2):
               print(str(self.count) + " " +
                     plural(self.count, "hasher"))

###################################

   def __getitem__(self, index):
      return(self.list[index])

###########################################################################

   @property
   def count(self):
      """
      use: Number of hashers belonging to us
      """
      return(len(self.list))

###########################################################################

   def add(self, hasher):
      """
      use: Add a hasher to our list of hashers. If the hasher to be added
           already belong to us, then a DuplicateError() exception will be
           raised
      see also: addUnique()
      """
      if (int(hasher.id) not in self.lookupIDs):
         self.list.append(hasher)
         self.lookupIDs[int(hasher.id)] = hasher
      else:
         raise DuplicateError("duplicate hasher ID")

###########################################################################

   def addUnique(self, hasher):
      """
      use: Add a hasher to our list of hashers. If the hasher to be added
           already belong to us, then nothing is done, and no exceptions
           will be raised
      see also: add()
      """
      try:
         self.add(hasher)
      except DuplicateError:
         pass

###########################################################################

   def getById(self, id):
      """
      use: Get a hasher by its hasher ID
      """
      return(self.lookupIDs[int(id)] if int(id) in self.lookupIDs
                                     else None)

###########################################################################

   def printBids(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: Print list of bids submitted by hashers belonging to us
      usage: See TimeSlots.printBids()
      """
      for hasher in self.list:
         hasher.printBids(indent, headLevel, detail)

###########################################################################

   def printHashers(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: Print list of hashers belonging to us
      usage: See TimeSlots.printBids()
      """
      for hasher in self.list:
         hasher.printHasher(indent, headLevel, detail)

###########################################################################

   def printResultByHasher(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: Print list of hashers belonging to us. If the hasher has one
           or more successful bids for trail, the trail information will
           be printed too
      usage: See TimeSlots.printBids()
      pre: runBid() processing must be completed
      """
      self.sortByName()
      for hasher in self.list:
         hasher.printResultByHasher(indent, headLevel, detail)

###########################################################################

   def printResultBySuccessfulHasher(self,
                                     indent = -1, headLevel = 0, detail = 0):
      """
      use: For every hasher with a successful bid for a trail, print the
           hasher and trail information of the successful bid
      usage: See TimeSlots.printBids()
      pre: runBid() processing must be completed
      """
      self.sortByName()
      for hasher in self.list:
         if (hasher.successfulBidCount > 0):
            hasher.printResultByHasher(indent, headLevel, detail)

###########################################################################

   def printResultByUnsuccessfulHasher(self,
                                     indent = -1, headLevel = 0, detail = 0):
      """
      use: For every hasher with a bid for a trail but was unsuccessful
           on all bids, print the hasher
      usage: See TimeSlots.printBids()
      pre: runBid() processing must be completed
      """
      self.sortByName()
      for hasher in self.list:
         if ((hasher.bidCount            > 0) and
             (hasher.successfulBidCount == 0)):
            hasher.printResultByHasher(indent, headLevel, detail)

###########################################################################

   def printResultByNoBidHasher(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: For every hasher without any bids for a trail, print the
           hasher
      usage: See TimeSlots.printBids()
      pre: runBid() processing should be completed
      """
      self.sortByName()
      for hasher in self.list:
         if (hasher.bidCount == 0):
            hasher.printResultByHasher(indent, headLevel, detail)

###########################################################################

   def sortById(self):
      """
      use: Sort our list of hashers according each hasher's ID number
      post: Our internal array of hashers is re-ordered and sorted by
            each hasher's ID number
      """
      self.list.sort(key = lambda hasher:hasher.id)

###################################

   def sortByName(self):
      """
      use: Sort our list of hashers according each hasher's name
      post: Our internal array of hashers is re-ordered and sorted by
            each hasher's name
      """
      self.list.sort(key = lambda hasher:hasher.name)

###################################

   def sortByOrder(self):
      """
      use: Sort our list of hashers according each hasher's order as
           assigned by sortByRandom()
      post: Our internal array of hashers is re-ordered and sorted by
            each hasher's order
      """
      self.list.sort(key = lambda hasher:hasher.order)

###################################

   def sortByRank(self):
      """
      use: Sort our list of hashers according each hasher's rank, which
           is calculated from its sequence and randomized order
      post: Our internal array of hashers is re-ordered and sorted by
            each hasher's rank
      see also: Bids.sortEquitably()
      """
      self.list.sort(key = lambda hasher:hasher.rank)

###################################

   def sortBySequence(self):
      """
      use: Sort our list of hashers according its sequence number
      post: Our internal array of hashers is re-ordered and sorted by
            each hasher's sequence number
      """
      self.list.sort(key = lambda hasher:hasher.sequence)

###################################

   def sortByRandom(self):
      """
      use: Sort the list of hashers randomly
      post: Our internal array of hashers is re-ordered and sorted by a
            rank, which is calculated from the hasher's sequence and a
            randomly assigned order
      imp: Bids are processed in order of their bid value. If a trail is
           oversubscribed, then the tie-breaker for awarding bid success
           for bids of equal value will be based on the bid's hasher's rank.
           Tie-breakers for equal-valued bids are not decided solely by
           the hasher's ID (which is sufficiently unique, and presumed to
           be their registration/rego number) because this would allow low
           ID hashers to trump all other hashers with higher IDs when
           bidding for trails. Low ID hashers will be enjoy some bidding
           advantages as a reward for registering early, but they will not
           be given absolute power to win bid tie-breakers.
      see also: Bids.sortEquitably()
      """
      random.shuffle(self.list)
      index = 0
      for hasher in self.list:
         index       += 1
         hasher.order = index
         hasher.rank  = hasher.sequence * hasher.sequence * hasher.order
      self.sortByRank()

###########################################################################
