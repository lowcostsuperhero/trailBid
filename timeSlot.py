# name: $Id: timeSlot.py 1 23:59:58 06-Apr-2021 rudyz $

import csv
import sys

import bid    as bid_module
import hasher as hasher_module
import trail  as trail_module

from resource import *
from setting  import *

###########################################################################
###########################################################################
###########################################################################
###
### t i m e    s l o t
###
###########################################################################
###########################################################################
###########################################################################

class TimeSlot:
   """
   use: A time slot is a period when one or more trails are scheduled to
        occur. Typically for an Interhash weekend, expect time slots for
        Friday, Saturday, and maybe Sunday, with multiple trails offered
        per time slot. Hashers can bid on multiple trails within a time
        slot, but their bids can be successful for only one trail per time
        slot, although they may be successful more than once at a rate of
        no more than one success per time slot
   imp: A time slot specifies when it and its trails are scheduled to occur.
        A trail supplies additional details for the run, such as the trail
        name, and capacity of how many hashers can attend the trail
   """
   def __init__(self, id, sequence, name):
      self.id       = str(id).strip()
      self.sequence = int(sequence)
      self.name     = name.strip()
     ###
      self.trails   = trail_module.Trails() # trails within this timeSlot

###################################

   def __str__(self):
      return(str(self.id) + ": " + self.name)

###########################################################################

   def addTrail(self, trail):
      """
      use: Add a trail to this timeSlot. This is nominally called by the
          calendar() function as part of reading the calendar.txt file
      """
      self.trails.add(trail)

###########################################################################

   def getBids(self):
      """
      use: All bids submitted for all the trails within this time slot
      """
      return(self.trails.getBids())

###########################################################################

   def getHashers(self):
      """
      use: All unique hashers who have submitted a bid for a trail within
           this time slot
      """
      return(self.trails.getHashers())

###########################################################################

   def prettyListDisplay(self):
      """
      use: A prettily formatted ID and name suitable for display in a list
           of time slots
      """
      return("{:<22s}".format("{:>3s}: {}".format(self.id, self.name)))

###########################################################################

   def printBids(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: Print list of all bids submitted for trails in this time slot
      usage: Optionally pass integer values for indent, headLevel, and
             detail:
                indent   : negative indent values prevents indenting by
                           child print*() methods we call
                headLevel: similar to HTML H1, H2, H3 tags, with lower
                           headLevel values more prominantly hightlighting
                           headings
                detail   : greater values of detail provide more details in
                           the print*() output
      """
      printHeading(str(self), indent, headLevel)
      self.trails.printBids(indent    + 1 if indent >= 0 else indent   ,
                            headLevel + 1 if headLevel   else headLevel,
                            detail)

###########################################################################

   def printHashers(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: Print list of all unique hashers who have submitted a bid for
           trails in this time slot
      usage: See TimeSlots.printBids()
      """
      printHeading(str(self), indent, headLevel)
      self.trails.printHashers(indent    + 1 if indent >= 0 else indent   ,
                               headLevel + 1 if headLevel   else headLevel,
                               detail)

###########################################################################

   def printTrails(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: Print list of all trails within this time slot
      usage: See TimeSlots.printBids()
      """
      printHeading(str(self), indent, headLevel)
      self.trails.printTrails(indent    + 1 if indent >= 0 else indent   ,
                              headLevel + 1 if headLevel   else headLevel,
                              detail)

###########################################################################

   def printResultByTrail(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: Print list of trails within this time slot, and list of hashers
           with a successful bid for the trail
      usage: See TimeSlots.printBids()
      pre: runBid() processing must be completed
      """
      printHeading(str(self), indent, headLevel)
      self.trails.printResultByTrail(
                     indent    + 1 if indent >= 0 else indent   ,
                     headLevel + 1 if headLevel   else headLevel,
                     detail)

###########################################################################

   def runBid(self):
      """
      use: Process the bids submitted for trails within this time slot
      """
      print(self.prettyListDisplay())
      self.trails.getHashers().sortByRandom()
      bids = bid_module.Bids()
                                # get a list of all bids from all trails in
                                # this time slot because each hasher can
                                # attend only one trail per time slot
      for trail in self.trails:
         bids.merge(trail.getBids())
      bids.runBid()

###########################################################################
###########################################################################
###########################################################################
###
### t i m e    s l o t s
###
###########################################################################
###########################################################################
###########################################################################

class TimeSlots:
   def __init__(self, filespec = None):
      self.list      = []
      self.lookupIDs = {} # dict keyed on lookup.id containing a timeSlot

      if (filespec is not None):
         if (os.path.isdir(filespec)):
            filespec = os.path.join(filespec, "timeSlots.txt")

         with open(filespec, "r") as csvfile:
            lineNumber = 0
            csvReader = csv.reader(csvfile)
            if (csv.Sniffer().has_header(open(csvfile.name).read(1024))):
               lineNumber += 1
               next(csvReader)
            for row in csvReader:
               lineNumber += 1
               if (len(row) != 0):
                  try:
                     timeSlot          = TimeSlot(row[0], row[1], row[2])
                     timeSlot.sequence = self.count + 1
                     self.add(timeSlot)
                     if (settings["verbosity"] != 0):
                        print(str(timeSlot))
                  except DuplicateError as exception:
                     if isinstance(exception, DuplicateError):
                        exception = "duplicate time slot ID"
                     writeFileReadError(filespec, lineNumber, exception,
                                        row[0] + ", " +
                                        row[1] + ", " + row[2])
                     printFileReadError(lineNumber, row[0] + ", " +
                                                    row[1] + ", " + row[2])
            if (settings["verbosity"] == 0):
               print(str(self.count) + " " +
                     plural(self.count, "time slot"))

###################################

   def __getitem__(self, index):
      return(self.list[index])

###################################

   @property
   def count(self):
      """use: Number of time slots belonging to us"""
      return(len(self.list))

###########################################################################

   def add(self, timeSlot):
      """
      use: Add a time slot to our list of time slots. If the time slot to
           be added already belongs to us, then the time slot will not be
           added and a DuplicateError() exception will be raised
      """
      if (int(timeSlot.id) not in self.lookupIDs):
         self.list.append(timeSlot)
         self.lookupIDs[timeSlot.id] = timeSlot
      else:
         raise DuplicateError("duplicate time slot ID")

###########################################################################

   def getById(self, id):
      """
      use: Get a time slot by its time slot ID
      """
      return(self.lookupIDs[id] if id in self.lookupIDs
             else None)

###########################################################################

   def getBids(self):
      """
      use: Get a Bids() object containing all bids submitted for trails
           in our time slots
      """
      result = bid_module.Bids()
      for timeSlot in self.list:
         result.merge(timeSlot.getBids())
      return(result)

###########################################################################

   def getHashers(self):
      """
      use: Get a Hashers() object containing all hashers who have submitted
           bids to trails within our time slots
      """
      result = hasher_module.Hashers()
      for timeSlot in self.list:
         for hasher in timeSlot.getHashers():
            result.addUnique(hasher)
      return(result)

###########################################################################

   def printBids(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: Print list of bids that have been submitted for trails within
           time slots belonging to us
      """
      for timeSlot in self.list:
         timeSlot.printBids(indent, headLevel, detail)

###########################################################################

   def printHashers(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: Print list of hashers who have submitted bids for trails in
           time slots belonging to us
      """
      nTimeSlot = 0
      for timeSlot in self.list:
         if (nTimeSlot):
            print()
         timeSlot.printHashers(indent, headLevel, detail)
         nTimeSlot += 1

###########################################################################

   def printTrails(self, indent = -1, headLevel = 0, detail = 0):
      """use: Print list of trails in our time slots"""
      nTimeSlots = 0
      for timeSlot in self.list:
         if (nTimeSlots):
            print()
         timeSlot.printTrails(indent, headLevel, detail)
         nTimeSlots += 1

###########################################################################

   def printResultByTrail(self, indent = -1, headLevel = 0, detail = 0):
      """
      use: For each time slot belonging to us, print list of trails and
           the hashers with a successful bid for the trail
      pre: runBid() processing must be completed
      """
      self.sortBySequence()
      nTimeSlots = 0
      for timeSlot in self.list:
         if (nTimeSlots):
            print()
            print()
         timeSlot.printResultByTrail(indent, headLevel, detail)
         nTimeSlots += 1

###########################################################################

   def runBid(self):
      """
      use: Process the bids submitted for all our time slots
      """
      for timeSlot in self.list:
         timeSlot.runBid()

###########################################################################

   def sortBySequence(self):
      """
      use: Sort the list of time slots by their sequence number
      post: Our internal array of time slots is re-ordered and sorted by the
            time slots' sequence number
      """
      self.list.sort(key = lambda timeSlot:timeSlot.sequence)
      return(self)

###########################################################################