# name: $Id: bid.py 12 20:31:49 08-Sep-2021 rudyz $

import csv
import sys

import bid      as bid_module
import hasher   as hasher_module
import timeSlot as timeSlot_module
import trail    as trail_module

from param    import *
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
       assert (isinstance(hasher, hasher_module.Hasher) and
               isinstance(trail , trail_module.Trail)), \
          "Bid constructor requires Hasher and Trail objects"
       self.hasher = hasher
       self.trail  = trail
       self.value  = int(value)

###################################

   def __str__(self):
      return(f"{self.hasher} -> {self.trail}; {self.value}")

###################################

   @property
   def timeSlot(self):
      """
      use: Time slot to which this trail belongs
      """
      return(self.trail.timeSlot)

###########################################################################

   def printBid(self, **kwargs):
      """
      use: Print list of bids belonging to us
      usage: See TimeSlots.printBids()
      """
      params = Params(kwargs, indent = -1,
                              detail =  0)
      params[self.__class__.__name__] = self

      if (params["detail"] >= 1):
         print(f"{'':>{max(params['indent'], 0)}}{self.hasher.pretty()} ~ "
               f"{self.value:>4d} -> {self.trail.pretty()}")
      else:
         print(f"{'':>{max(params['indent'], 0)}}{self.hasher.pretty()} -> "
               f"{self.trail.pretty()}")

###########################################################################

   def printHasher(self, **kwargs):
      """
      use: Print hasher who submitted this bid
      usage: See TimeSlots.printBids()
      """
      params = Params(kwargs, indent    = -1,
                              headLevel =  0,
                              detail    =  0)
      params[self.__class__.__name__] = self

      if ((params["outputFormat"] is None) or
          (params["outputFormat"] in ("roster", "html"))):
         self.hasher.printHasher(**params())
      else:
         sys.stderr.write(f"{selfName}: Bid.printResultByTrail(): "
                          f"unknown output format: "
                          f"{params['outputFormat']}\n")

###########################################################################

   def printTrail(self, **kwargs):
      """
      use: Print trail that is bidded on by this bid
      usage: See TimeSlots.printBids()
      """
      params = Params(kwargs, indent    = -1,
                              headLevel =  0,
                              detail    =  0)
      params[self.__class__.__name__] = self

      if ((params["outputFormat"] is None  ) or
          (params["outputFormat"] == "html")):
         self.trail.printTrail(**params())
      else:
         sys.stderr.write(f"{selfName}: Bid.printTrail(): "
                          f"unknown output format: "
                          f"{params['outputFormat']}\n")

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
                              f"{str(hasher)} -> {str(trail)}")
                     else:
                        bid = Bid(hasher, trail, value)
                        self.add(bid)
                        if (settings["verbosity"] >= 3):
                           print(str(bid))
                        hasher.addBid(bid)
                        trail.addBid(bid)
                  except Exception as exception:
                     writeFileReadError(filespec, lineNumber, exception,
                                        f"{str(hasher)} -> {str(trail)}")
                     printFileReadError(lineNumber,
                                        f"{str(hasher)} -> {str(trail)}")
                     raise
            if (settings["verbosity"] < 3):
               print(f"{self.count} {plural(self.count, 'bid')}")

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
      use: All your bids are belong to us
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

   def printBids(self, **kwargs):
      """
      use: Print list of bids belonging to us
      usage: See TimeSlots.printBids()
      """
      params = Params(kwargs, indent    = -1,
                              headLevel = 0,
                              detail    = 0)
      params[self.__class__.__name__] = self

      for bid in self.list:
         bid.printBid(**params())

###########################################################################

   def printHashers(self, **kwargs):
      """
      use: Print list of hashers who have submitted a bid belonging to
           us
      usage: See TimeSlots.printBids()
      """
      params = Params(kwargs, detail = 0)
      params[self.__class__.__name__] = self

      if (params["outputFormat"] == "html"):
         nHasher = 0
         for index in range(0, self.count):
            if (nHasher == 0):
               params["outputFile"].write("  <tr>\n")
            self.list[index].printHasher(**params())
            nHasher += 1
            if ((nHasher % 3) == 0):
               params["outputFile"].write("  </tr>\n")
               nHasher = 0
         if (nHasher != 0):
            params["outputFile"].write("  </tr>\n")
      elif (params["outputFormat"] == "roster"):
         virtualHasher = hasher_module.Hasher(0, 0, "")
         virtualBid    = bid_module.Bid(virtualHasher, None, 0)
         nHasher = 0
         for index in range(0, params["Trail"].capacity):
            if (nHasher == 0):
               params["outputFile"].write("  <tr>\n")
            if (index < self.count):
               self.list[index].printHasher(**params())
            else:
               virtualHasher.id = index + 1
               virtualBid.printHasher(**params())
            nHasher += 1
            if ((nHasher % 3) == 0):
               params["outputFile"].write("  </tr>\n")
               nHasher = 0
         if (nHasher != 0):
            params["outputFile"].write("  </tr>\n")
      elif (params["outputFormat"] is None):
         params.setDefaults(indent    = -1,
                            headLevel =  0)
         for bid in self.list:
            bid.printHasher(**params())
      else:
         sys.stderr.write(f"{selfName}: Bids.printHashers():"
                          f" unknown output format: "
                          f"{params['outputFormat']}\n")

###########################################################################

   def printTrails(self, **kwargs):
      """
      use: Print list of trails which have been bidded on by a bid
           belonging to us
      usage: See TimeSlots.printBids()
      """
      params = Params(kwargs, indent    = -1,
                              headLevel =  0,
                              detail    =  0)
      params[self.__class__.__name__] = self

      for bid in self.list:
         bid.printTrail(**params())

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

   def sortByTrail(self):
      """
      use: Sort our list of bids according each bid's trail's time slot
           sequence and trail sequence
      post: Our internal array of bids is re-ordered and sorted by each
            bid's trail's time slot sequence and trail sequence
      """
      self.list.sort(key = lambda bid:(bid.trail.timeSlot.sequence,
                                       bid.trail.sequence))

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
                slight advantage over hashers who have more number of
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
                        bid.trail.id)) # bidCount comes into play when the
                        # trail becomes oversubscribed, so we try to fulfill
                        # trails with fewer submitted bids first so that we
                        # we can delay filling up the trail with more bids
                        # submitted for it, and hopefully will allow us to
                        # successfully satisfy more bids
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
