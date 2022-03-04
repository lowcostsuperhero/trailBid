# name: $Id: trail.py 15 20:55:29 08-Sep-2021 rudyz $

import csv
import sys

import bid    as bid_module
import hasher as hasher_module

from param    import *
from resource import *
from setting  import *

###########################################################################
###########################################################################
###########################################################################
###
### t r a i l
###
###########################################################################
###########################################################################
###########################################################################

class Trail:
   """
   use: A trail belongs to exactly one time slot. Hashers indicate their
        desire to attend a trail by submitting a bid for the trail
   imp: Trails belong to a time slot, which specifies when its trails are
        scheduled to occur. A trail supplies additional details for the run,
        such as the trail name, and capacity of how many hashers can attend
        the trail
   """
   def __init__(self, id, sequence, name, capacity):
       self.id             = str(id).strip()
       self.sequence       = int(sequence)
       self.name           = name.strip()
       self.capacity       = int(capacity)
      ###
       self.timeSlot       = None
       self.bids           = bid_module.Bids()
       self.successfulBids = bid_module.Bids()

###################################

   def __str__(self):
       return(f"{self.id}: {self.name}")

###########################################################################

   @property
   def successfulBidsCount(self):
      """
      use: Number of winning bids from hashers who will participating in
           this trail
      """
      return(self.successfulBids.count)

###################################

   @property
   def successfulBookendValues(self):
      """
      use: Lowest and highest values of successful bids belonging to us
      post: Return value is a tuple of two element
      """
      return(self.successfulBids.bookendValues)

###################################

   @property
   def bidCount(self):
      """
      use: Number of bids for this trail submitted by hashers wanting to
           participate in this trail
      """
      return(len(self.bids.list))

###################################

   @property
   def bidValue(self):
      """
      use: Sum of values for all bids submitted for this trail
      """
      return(sum(bid.value for bid in self.bids.list)
             if self.bidCount > 0 else 0)

###################################

   def getTimeSlot(self):
      """
      use: Property getter method returning the time slot to which this
           trail belongs
      """
      return(self._timeSlot)
   def setTimeSlot(self, timeSlot):
      """
      use: Property setter method assigning the time slot to which this
           trail belongs. The source of this relationship is usually from
           the calendar.txt file
      imp: Sets a time slot if the time slot has not been set. Attempts to
           set a trail's time slot if its time slot has already been set
           will result in a DuplicateError() exception. This is because
           a trail's relation to its time slot is permanent, and once
           established, it is never expected to change
      post: Timeslot for this trail will be set, or an exception will be
            raised that the time slot has already been set
      """
      if (('_timeSlot' not in self.__dict__) or
          (self._timeSlot is None) or
          (timeSlot       is None)):
         self._timeSlot = timeSlot
      else:
         raise(DuplicateError(f"\n"
            f"   trail already has time slot\n"
            f"   >>> {str(self)}"))
   timeSlot = property(getTimeSlot, setTimeSlot)

###########################################################################

   def addBid(self, bid):
      """
      use: Add a hasher's bid to this trail
      """
      self.bids.add(bid)

###########################################################################

   def addSuccessfulBid(self, bid):
      """
      use: Usually called by runBid() method to add a hasher's winning bid
           for this trail
      """
      self.successfulBids.add(bid)

###########################################################################

   def getBids(self):
      """use: All bids submitted for this trail"""
      return(self.bids.getBids())

###########################################################################

   def isAtCapacity(self):
      """
      use: Predicate indicating if this trail is already at capacity and no
           more additional hashers should be allowed to be added to this
           trail
      """
      return(self.successfulBids.count >= self.capacity)

###########################################################################

   def getHashers(self):
      """use: All hashers who have submitted a bid for this trail"""
      return(self.bids.getHashers())

###########################################################################

   def printBids(self, **kwargs):
      """
      use: Print list of all bids submitted for this trail
      usage: See TimeSlots.printBids()
      """
      params = Params(kwargs, indent    = -1,
                              headLevel =  0,
                              detail    =  0)
      params[self.__class__.__name__] = self

      self.bids.printBids(**params())

###########################################################################

   def printHashers(self, **kwargs):
      """
      use: Print list of all hashers who have submitted a bid for this
           trail
      usage: See TimeSlots.printBids()
      """
      params = Params(kwargs, indent    = -1,
                              headLevel =  0,
                              detail    =  0)
      params[self.__class__.__name__] = self

      printHeading(self.name, params["indent"], params["headLevel"])

      if (params["indent"   ] >= 0):
         params["indent"   ] = params["indent"   ] + 1
      if (params["headLevel"] >  0):
         params["headLevel"] = params["headLevel"] + 1
      self.bids.printHashers(**params())

###########################################################################

   def printTrail(self, **kwargs):
      """
      use: Print, at minimum, this trail's ID and name
      usage: See TimeSlots.printBids().
             For detail passed as a non-zero value:
                1: also print trail capacity
                2: also print bid count, trail capacity, and total bid value
      """
      params = Params(kwargs, indent    = -1,
                              headLevel =  0,
                              detail    =  0)
      params[self.__class__.__name__] = self

      if (params["outputFormat"] == "html"):
         nbsp = "&nbsp;" * (params["indent"] or 0)
         params["outputFile"].write(f"    {nbsp}{str(self)}<br/>\n")
      elif (params["outputFormat"] is None):
         if (params["detail"] >= 2):
            print(f"{'':>{max(params['indent'], 0)}}{self.pretty()}"
                  f" [{self.bidCount:>5d}/{self.capacity:<5d}"
                  f" ~{self.bidValue:<7d}]")
         else:
            bid = None
            if (params["detail"] > 0):
               bid = params["Bid"]
            if (bid is None):
               print(f"{'':>{max(params['indent'], 0)}}{self.pretty()}")
            else:
               print(f"{'':>{max(params['indent'], 0)}}"
                     f"{self.pretty()} ~ {bid.value:4d}")
      else:
         sys.stderr.write(f"{selfName}: Trail.printTrail(): "
                          f" unknown output format: "
                          f"{params['outputFormat']}\n")


###########################################################################

   def printResultByTrail(self, **kwargs):
      """
      use: Print list of hashers with a successful bid for this trail.
      usage: See TimeSlots.printBids().
             Additional optional Params() argument that can be passed is:
                outputFormat: one of the following:
                   roster the intent of a roster is to produce a hardcopy
                          output for a bus captain to check-in hashers
                          going on trail
                   html   similar to roster, but without checkboxes.
                          suitable for inclusion on a website
                   None   simple text output list
      """
      params = Params(kwargs, indent    = -1,
                              headLevel =  0,
                              detail    =  0)
      params[self.__class__.__name__] = self

      (lowest, highest) = self.successfulBids.bookendValues
      if (params["outputFormat"] in ("roster", "html")):
         outputDirectory = os.path.join(settings["eventDirectory"], "html")
         if (not os.path.isdir(outputDirectory)):
            os.mkdir(outputDirectory)
         if (params["outputFormat"] == "roster"):
            outputFilename = (f"{self.id}-"
                              f"{self.name.title().replace(' ', '').strip()}"
                              f"-roster.html")
         else:
            outputFilename = (f"{self.id}-"
                              f"{self.name.title().replace(' ', '').strip()}"
                              f".html")
         outputFile = os.path.join(outputDirectory, outputFilename)
         params["outputFile"] = open(outputFile, "w")
         params["outputFile"].writelines(
            ["<!DOCTYPE html>\n"                                   ,
             "<html>\n"                                            ,
             "<head>\n"])
         if (params["outputFormat"] == "roster"):
            params["outputFile"].writelines(
               [" <style>\n"                                        ,
                "  p.timeslot {font-size: 20px; margin-bottom: 0}\n",
                "  p.trail    {font-size: 30px;"          +
                             " margin-top: 0; margin-bottom: 5pt}\n",
                "  table, td  {border: 1px solid black;"  +
                             " border-collapse: collapse}\n"        ,
                "  div.left   {float: left; text-align: left}\n"    ,
                "  div.right  {float: right; text-align: right}\n"  ,
                " </style>\n"])
         else:
            params["outputFile"].writelines(
               [" <style>\n"                                        ,
                "  p.timeslot {font-size: 20px; margin-bottom: 0}\n",
                "  p.trail    {font-size: 30px;"          +
                             " margin-top: 0; margin-bottom: 5pt}\n",
                " </style>\n"])
         params["outputFile"].writelines(
             [" <title>" + str(self) + "</title>\n"                         ,
              "</head>\n"                                                   ,
              "\n"                                                          ,
              "<body>\n"                                                    ,
              "<p class=timeslot>" + self.timeSlot.name + "</p>\n"          ,
              "<p class=trail><b>" + str(self)          + "</b></p>\n"      ,
              "<b>Attendees: "     + str(self.successfulBidsCount) + "/" +
                                     str(self.capacity) + "</b><br/><br/>\n",
              ' <table cellpadding=5pt style="width: 7.5in">\n'])
         self.successfulBids.sortByHasherName()
         self.successfulBids.printHashers(**params())
         params["outputFile"].writelines(
            [" </table>\n",
             "</body>\n",
             "</html>\n"])
         params["outputFile"].close()
         params["outputFile"] = None
      elif (params["outputFormat"] is None):
         printHeading(self.name, params["indent"], params["headLevel"])
         printHeading(f"- Attendees = "
                      f"{self.successfulBidsCount}/{self.capacity}; "
                      f"bid range = {highest}~{lowest}",
                      params["indent"], params["headLevel"])
         self.successfulBids.sortByHasherName()

         if (params["indent"   ] >= 0):
            params["indent"   ] = params["indent"   ] + 1
         if (params["headLevel"] >  0):
            params["headLevel"] = params["headLevel"] + 1
         self.successfulBids.printHashers(**params())
      else:
         sys.stderr.write(f"{selfName}: Trail.printResultByTrail(): "
                          f"unknown output format: "
                          f"{params['outputFormat']}\n")

###########################################################################

   def pretty(self):
      """
      use: A prettily formatted ID and name suitable for display in a list
           of trails
      """
      return(f"{f'{self.id:>3}: {self.name}':<22}")

#    def setTimeSlot(self, timeSlot):
#       if (self.timeSlot is None):
#          self.timeSlot = timeSlot
#       else:
#          raise AlreadyDoneError("trail already has time slot set")

###########################################################################

   def runBid(self):
      """
      use: Process all bids submitted for our trails
      imp: Bid will be successful if the trail is not at capacity and has
           vacancies available, and the hasher does not already have a
           successful bid for another trail in the same time slot.
      post: If the bid is successful, the successful bid will be added to
            this trail's list of successful bids as well as to the hasher's
            list of successful bids. If the trail is already at capacity,
            a message attesting to that will be printed and nothing else
            will be done for the bid, hasher, or trail
      """
      print(str(self))
      for bid in self.bids.sortEquitably():
         if (self.successfulBidsCount < self.capacity):
            if (self.successfulBids.getByHasherId(bid.hasher.id) is None):
               hasherTrails = bid.hasher.successfulBids.getTrailsByTimeSlotId(
                                 self.timeSlot.id)
               if (hasherTrails.count == 0):
                  print(f"{str(bid.hasher)} ~ {bid.value}")
                  self.successfulBids.add(bid)
                  bid.hasher.successfulBids.add(bid)
               else:
                  print(f"   {str(bid.hasher)} -> {hasherTrails[0].id}")
         if (self.successfulBidsCount >= self.capacity):
            print(f"trail {str(self)} reached capacity")
            break

###########################################################################
###########################################################################
###########################################################################
###
### t r a i l s
###
###########################################################################
###########################################################################
###########################################################################

class Trails:
   def __init__(self, filespec = None):
      """
      usage: Optionally pass an event directory name in which a data file
             for trails is stored
      """
      self.list      = []
      self.lookupIDs = {}

      if (filespec is not None):
         if (os.path.isdir(filespec)):
            filespec = os.path.join(filespec, "trails.txt")

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
                     trail = Trail(row[0], row[1], row[2], row[3])
                     self.add(trail)
                     if (settings["verbosity"] != 0):
                        print(str(trail))
#                   except (ValueError, DuplicateError) as exception:
                  except DuplicateError as exception:
                     if isinstance(exception, DuplicateError):
                        exception = "duplicate trail ID"
                     writeFileReadError(
                        filespec, lineNumber, exception,
                        f"{row[0]}, {row[1]}, {row[2]}, {row[2]}")
                     printFileReadError(
                        lineNumber,
                        f"{row[0]}, {row[1]}, {row[2]}, {row[2]}")
            if (settings["verbosity"] == 0):
               print(f"{self.count} {plural(self.count, 'trail')}")

###################################

   def __getitem__(self, index):
      return(self.list[index])

###################################

   @property
   def count(self):
      """
      use: Number of trails belonging to us
      """
      return(len(self.list))

###################################

   @property
   def successfulBookendValues(self):
      """
      use: Lowest and highest values of successful bids belonging to us
      post: Return value is a tuple of two element
      """
      return(self.successfulBids.bookendValues)

###########################################################################

   def add(self, trail):
      """
      use: Add a trail to our list of trails. If the trail to be added
           already belongs to us, then the trail will not be added and a
           DuplicateError() exception will be raised
      see also: addUnique()
      """
      if (trail.id not in self.lookupIDs):
         self.list.append(trail)
         self.lookupIDs[trail.id] = trail
      else:
         raise DuplicateError("duplicate trail ID")

###########################################################################

   def addUnique(self, trail):
      """
      use: Add a trail to our list of trails. If the trail to be added
           already belongs to us, then nothing is done, and no exceptions
           will be raised
      see also: add()
      """
      try:
         self.add(trail)
      except DuplicateError:
         pass

###########################################################################

   def getBids(self):
      """
      use: All bids submitted for all the trails belonging to us
      """
      result = bid_module.Bids()
      for trail in self.list:
         result.merge(trail.getBids())
      return(result)

###########################################################################

   def getById(self, id):
      """
      use: Get a trail by its trail ID
      """
      return(self.lookupIDs[id] if id in self.lookupIDs else None)

###########################################################################

   def getHashers(self):
      """
      use: All hashers who have submitted a bid for a trail belonging to us
      """
      result = hasher_module.Hashers()
      for trail in self.list:
         for hasher in trail.getHashers():
            result.addUnique(hasher)
      return(result)

###########################################################################

   def getTrailsByTimeSlotId(self, timeSlotId):
      """
      use: All trails belonging to the time slot corresponding to the passed
           timeSlotId
      """
      result = Trails()
      for trail in self.list:
         if (trail.timeSlot.id == timeSlotId):
            result.addUnique(trail)
      return(result)

###########################################################################

   def printBids(self, **kwargs):
      """
      use: Print list of all bids received for trails belonging to us
      usage: See TimeSlots.printBids()
      """
      params = Params(kwargs, indent    = -1,
                              headLevel =  0,
                              detail    =  0)
      params[self.__class__.__name__] = self

      for trail in self.list:
         trail.printBids(**params())

###########################################################################

   def printHashers(self, **kwargs):
      """
      use: Print list of all hashers who have submitted bids for trails
           belonging to us
      usage: See TimeSlots.printBids()
      """
      params = Params(kwargs, indent    = -1,
                              headLevel =  0,
                              detail    =  0)
      params[self.__class__.__name__] = self

      nTrails = 0
      for trail in self.list:
         if (nTrails):
            print()
         trail.printHashers(**params())
         nTrails += 1

###########################################################################

   def printResultByTrail(self, **kwargs):
      """
      use: For each trail, print list of hashers with a successful bid for
           the trail
      usage: See TimeSlots.printBids()
      """
      params = Params(kwargs, detail =  0)
      params[self.__class__.__name__] = self

      if (params["outputFormat"] in ("roster", "html")):
         for trail in self.sortBySequence():
            trail.printResultByTrail(**params())
      elif (params["outputFormat"] is None):
         params.setDefaults(indent    = -1,
                            headLevel =  0)
         if (params["indent"   ] >= 0):
            params["indent"   ] = params["indent"   ] + 1
         if (params["headLevel"] >  0):
            params["headLevel"] = params["headLevel"] + 1

         nTrails = 0
         for trail in self.sortBySequence():
            if (nTrails):
               print()

            trail.printResultByTrail(**params())
            nTrails += 1
      else:
         sys.stderr.write(f"{selfName}: Trails.printResultByTrail(): "
                          f" unknown output format: "
                          f"{params['outputFormat']}\n")

###########################################################################

   def printTrails(self, **kwargs):
      """
      use: Print list of trails belonging to us
      usage: See TimeSlots.printBids()
      """
      params = Params(kwargs, indent    = -1,
                              headLevel =  0,
                              detail    =  0)
      params[self.__class__.__name__] = self

      for trail in self.list:
         trail.printTrail(**params())

###########################################################################

   def runBid(self):
      """
      use: Process the bids submitted for trails belonging to us
      """
      for trail in self.sortByBidValue():
         trail.runBid()

###########################################################################

   def sortByBidValue(self):
      """
      use: Sort our list of trails according each bid's value
      post: Our internal array of trails is re-ordered and sorted by
            each trail's bid value and number of bids submitted for the
            trail
      see also: Bids.sortEquitably()
      """
      self.list.sort(key = lambda trail:(-trail.bidValue,
                                         trail.bidCount ,
                                         trail.id))
      return(self.list)

###########################################################################

   def sortBySequence(self):
      """
      use: Sort our list of trails according each trail's sequence
           number
      post: Our internal array of trails is re-ordered and sorted by
            each trail's sequence number
      """
      self.list.sort(key = lambda trail:trail.sequence)
      return(self.list)

###########################################################################
