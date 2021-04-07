# name: $Id: bid.py 1 23:59:55 06-Apr-2021 rudyz $

import csv
import sys

import bid      as bid_module
import hasher   as hasher_module
import timeSlot as timeSlot_module
import trail    as trail_module

from resource import *
from setting  import *

###########################################################################
###########################################################################
###########################################################################
###
### b i d
###
###########################################################################
###########################################################################
###########################################################################

class Bid:
   """
   use: A bid is the hub of a hasher, a bid value, and a trail
   """
   def __init__(self, hasher, trail, value):
       self.hasher = hasher
       self.trail  = trail
       self.value  = int(value)

###################################

   def __str__(self):
      return(str(self.hasher) + ' -> ' +
             str(self.trail ) + '; '   +
             str(self.value))

###################################

   @property
   def timeSlot(self):
      """
      use: Time slot to which this trail belongs
      """
      return(self.trail.timeSlot)

###########################################################################

   def printBid(self, indent = -1, detail = 0):
      """
      use: Print list of bids belonging to us
      usage: See TimeSlots.printBids()
      """
      if (detail >= 1):
         print("".ljust(max(indent, 0))                 +
               self.hasher.prettyListDisplay() + " ~ "  +
               "{:>4d}".format(self.value)     + " -> " +
               self.trail.prettyListDisplay())
      else:
         print("".ljust(max(indent, 0))                 +
               self.hasher.prettyListDisplay() + " -> " +
               self.trail.prettyListDisplay())

###########################################################################

   def printHasher(self, indent = -1, detail = 0):
      """
      use: Print hasher who submitted this bid
      usage: See TimeSlots.printBids()
      """
      if (detail >= 1):
         print("".ljust(max(indent, 0))                 +
               self.hasher.prettyListDisplay() + " ~ "  +
               "{:>4d}".format(self.value))
      else:
         print("".ljust(max(indent, 0)) +
               self.hasher.prettyListDisplay())

###########################################################################

   def printTrail(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: Print trail that is bidded on by this bid
      usage: See TimeSlots.printBids()
      """
      if (detail >= 1):
         print("".ljust(max(indent, 0)) +
               "{} ~ {:>4d}".format(self.trail.prettyListDisplay(),
                                    self.value))
      else:
        self.trail.printTrail(indent, 0)

###########################################################################

   def runBid(self):
      """
      use: Process this bid
      post: If this bid is successful, then both the trail and hasher will
            have this trail added to their list of successful bids. if the
            bid is unsuccessful, nothing is done
      imp: If the trail is not at capacity and still has vacancies, and
           the hasher has not successfully bid on another trail in this
           same time slot, then this bid will be successful.
      """
      if ((not self.trail.isAtCapacity()) and
          (not self.hasher.isAttendingTimeSlot(self.timeSlot.id))):
         self.trail.addSuccessfulBid(self)
         self.hasher.addSuccessfulBid(self)

###########################################################################
###########################################################################
###########################################################################
###
### b i d s
###
###########################################################################
###########################################################################
###########################################################################

class Bids:
   def __init__(self, filespec = None, hashers = None, trails = None):
      self.list         = []
      self.hasherBids   = {} # dict keyed on bid.hasher.id, containing an
                             # array of bids
      self.trailBids    = {} # dict keyed on bid.trail.id, containing an
                             # array of bids
      self.timeSlotBids = {} # dict keyed on bid.timeSlot.id, containing
                             # an array of bids

      if (filespec is not None):
         if (os.path.isdir(filespec)):
            filespec = os.path.join(filespec, "bids.txt")

         with open(filespec, "r") as csvfile:
            lineNumber = 0
            csvReader  = csv.reader(csvfile)
            if (csv.Sniffer().has_header(open(csvfile.name).read(1024))):
               lineNumber += 1
               next(csvReader)
            for row in csvReader:
               lineNumber += 1
               if (len(row) != 0):
                  try:
                     hasher = hashers.getById(int(row[0]))
                     trail  = trails.getById(str(row[1]).lstrip())
                     value  = int(row[2])
                     if ((hasher is None) or
                         (trail  is None)):
                                # carve out for lineNumber 1 where timeSlot
                                # and trail are both None is probably a
                                # header that the csv.Sniffer failed to detect
                        if (not ((lineNumber == 1) and
                                 (hasher is None ) and
                                 (trail  is None ))):
                           printFileReadError(
                              lineNumber,
                              str(hasher) + " -> " + str(trail))
                     else:
                        bid = Bid(hasher, trail, value)
                        self.add(bid)
                        if (settings["verbosity"] >= 2):
                           print(str(bid))
                        hasher.addBid(bid)
                        trail.addBid(bid)
                  except Exception as exception:
                     writeFileReadError(filespec, lineNumber, exception,
                                        str(hasher) + " -> " + str(trail))
                     printFileReadError(lineNumber,
                                        str(hasher) + " -> " + str(trail))
                     raise
            if (settings["verbosity"] < 2):
               print(str(self.count) + " " +
                     plural(self.count, "bid"))

###################################

   def __getitem__(self, index):
      return(self.list[index])

###################################

   @property
   def bookendValues(self):
      """
      use: Lowest and highest values of bids belonging to us
      post: Return value is a tuple of two element
      """
      return(min(self.list,
                 key=lambda b:b.value).value if self.count > 0 else None,
             max(self.list,
                 key=lambda b:b.value).value if self.count > 0 else None)

###################################

   @property
   def count(self):
      """use: Number of bids belonging to us"""
      return(len(self.list))

###################################

   @property
   def value(self):
      """use: Sum of values for all bids belonging to us"""
      return(sum(bid.value for bid in self.list) if self.count > 0 else 0)

###########################################################################

   def add(self, bid):
      """
      use: Add a bid to our internal dictionary of hashers, trails, and
           bids
      post: Affected hashers, trails, and bids will have their internal
            collections updated to track their related objects
      """
      self.list.append(bid)
      hasherId = int(bid.hasher.id)
      if (hasherId not in self.hasherBids):
         self.hasherBids[int(hasherId)] = []
      self.hasherBids[int(hasherId)].append(bid)
      trailId = bid.trail.id.strip()
      if (trailId not in self.trailBids):
         self.trailBids[trailId] = []
      self.trailBids[trailId].append(bid)
      timeSlotId = bid.trail.timeSlot.id
      if (timeSlotId not in self.timeSlotBids):
         self.timeSlotBids[timeSlotId] = []
      self.timeSlotBids[timeSlotId].append(bid)

###########################################################################

   def getBids(self):
      """
      use: All bids belonging to us
      """
      return(Bids().merge(self))

###########################################################################

   def getBidsByHasherId(self, hasherId):
      """
      use: All bids submitted by hasher corresponding to passed hasherId
      """
      result = bid_module.Bids()
      if (int(hasherId) in self.hasherBids):
         result.merge(self.hasherBids[int(hasherId)])
      return(result)

###########################################################################

   def getBidsByTimeSlotId(self, timeSlotId):
      """
      use: All bids submitted to trails belonging to time slot
           corresponding to passed time slot ID
      """
      result = bid_module.Bids()
      if (timeSlotId in self.timeSlotBids):
         result.merge(self.timeSlotBids[timeSlotId])
      return(result)

###########################################################################

   def getBidsByTrailId(self, trailId):
      """
      use: All bids submitted to trail corresponding to passed time
           trail ID
      """
      result = bid_module.Bids()
      if (trailId in self.trailBids):
         for bid in self.trailBids[trailId]:
            result.add(bid)
      return(result)

###########################################################################

   def getHashersByTimeSlotId(self, timeSlotId):
      """
      use: All hashers who have submitted bids for trails belonging to
           time slot corresponding to passed time slot ID
      """
      result = hasher_module.Hashers()
      for bid in self.getBidsByTimeSlotId(timeSlotId).list:
         result.addUnique(bid.hasher)
      return(result)

###########################################################################

   def getTimeSlots(self):
      """
      use: All time slots to which our bidded-on trails belong
      """
      result = timeSlot_module.TimeSlots()
      for bid in self.list:
         if (bid.timeSlot not in result):
            result.add(bid.timeSlot);
      return(result)

###########################################################################

   def getTrailsByTimeSlotId(self, timeSlotId):
      """
      use: All trails belonging to time slot corresponding to passed
           time slot ID
      """
      result = trail_module.Trails()
      for bid in self.getBidsByTimeSlotId(timeSlotId).list:
         if (result.getById(bid.trail.id) is None):
            result.add(bid.trail)
      return(result)

###########################################################################

   def getHashers(self):
      """
      use: All hashers who have submitted bids belonging to us
      """
      result = hasher_module.Hashers()
      for bid in self.list:
         result.addUnique(bid.hasher)
      return(result)

###########################################################################

   def merge(self, bids):
      """
      use: Add all bids in the passed bids object into our list of bids
      """
      for bid in bids:
         self.add(bid)
      return(self)

###########################################################################

   def printBids(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: Print list of bids belonging to us
      usage: See TimeSlots.printBids()
      """
      for bid in self.list:
         bid.printBid(indent, detail)

###########################################################################

   def printHashers(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: Print list of hashers who have submitted a bid belonging to
           us
      usage: See TimeSlots.printBids()
      """
      for bid in self.list:
         bid.printHasher(indent, detail)

###########################################################################

   def printTrails(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: Print list of trails which have been bidded on by a bid
           belonging to us
      usage: See TimeSlots.printBids()
      """
      for bid in self.list:
         bid.printTrail(indent, headLevel, detail)

###########################################################################

   def runBid(self):
      """
      use: Process the bids that belong to us
      """
      self.sortEquitably()
      for bid in self.list:
         bid.runBid()

###########################################################################

   def sortByHasherName(self):
      """
      use: Sort our list of bids according each bid's hasher's name
      post: Our internal array of bids is re-ordered and sorted by each
            bid's hasher's name
      """
      self.list.sort(key = lambda bid:(bid.hasher.name,
                                       bid.hasher.id))
      return(self.list)

###########################################################################

   def sortEquitably(self):
      """
      use: Sort our list of bids according to a each bid's value, and a
           hierachical set of attributes
      post: Our internal array of bids is re-ordered and sorted by a
            calculated rank
      imp: Sort bids into a working order:
              - Bids with higher bid values first, then progressing through
                other attributes.
              - Hashers with fewer successful bids and fewer bids have a
                slight advantage over hashers who have been more number of
                successful bids, or have more bids that would give them a
                greater number of chances to be successful later
              - The randomized hasher sequence number, so that the hasher
                with lowest ID (sequence) of one won't be able to trump all
                others by bidding the maximum amount on their favored trail
              - Less bidded-on trails get filled first to reduce the demand
                on the more bidded-on trails
           All these additional sorting attributes only come into play as a
           tie-breaker within all the bids with equal bid values
      see also: Hashers.sortByRandom()
      """
      self.list.sort(key = lambda bid:(
                        -bid.value                   , # higher bid value 1st
                        bid.hasher.successfulBidCount, # favor less successful
                        bid.hasher.bidCount          , # advantage fewer bids
                        bid.hasher.rank              , # randomized rank
                        bid.trail.bidCount           , # less bidded-on trails
                        bid.trail.id))
      return(self)

###########################################################################

   def valueByTimeSlotId(self, timeSlotId):
      """
      use: Sum of values for all bids belonging to the time slot
           corresponding to the passed timeSlotId
      """
      return(sum(bid.value for bid in self.timeSlotBids[timeSlotId])
             if (timeSlotId in self.timeSlotBids) else 0)

###########################################################################
