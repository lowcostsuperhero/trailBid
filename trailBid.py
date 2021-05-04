# name: $Id: trailBid.py 9 00:51:41 04-May-2021 rudyz $
"""
usage: Default execution is
          python trailBid.py
       To remain in interactive mode after importing trailBid.py:
          python -i trailBid.py eventDirectory
       In interactive mode, "help()" will get a small amount of help
pre: If trails, hashers, or bids have changed, the 00-orderOfHashers.txt
     file in the event directory should be removed prior to the next
     call to runBid()
"""
import getopt
import posixpath
import sys

from param    import *
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
         self.timeSlots.printTrails(Params([("indent"   , 0),
                                            ("headLevel", 2),
                                            ("detail"   , 2)]))
      if (settings["verbosity"] >= 3):
         print()
         printHeading("/// time slot bids ///", 0, 1)
         self.timeSlots.printBids(Params([("indent"     , 0),
                                          ("headLevel", 2),
                                          ("detail"   , 1)]))
      if (settings["verbosity"] >= 3):
         print()
         printHeading("/// time slot hashers ///", 0, 1)
         self.timeSlots.printHashers(Params([("indent"   , 0),
                                             ("headLevel", 2),
                                             ("detail"   , 1)]))
      if (settings["verbosity"] >= 3):
         print()
         printHeading("/// time slot unique hashers ///", 0, 1)
         for timeSlot in self.timeSlots:
            printHeading(str(timeSlot), indent = 0, headLevel = 2)
            timeSlot.getHashers().printHashers(Params([("indent"   , 1),
                                                       ("headLevel", 3),
                                                       ("detail"   , 1)]))

      if (settings["verbosity"] >= 3):
         print()
         printHeading("/// hasher bids ///", 0, 1)
         self.hashers.printBids(Params("indent", 0))

###########################################################################

   def runBid(self):
      """
      use: Process bid data, awarding trails to hashers who have submitted
           bids to attend trails
      """
      printHeading("/// run bid ///", 0, 1)
      self.hashers.sortByRandom()
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

   def printResultByHasher(self, params = Params()):
      """
      use: For every hasher who has submiited one or more bids, print the
           hasher and trail information of the successful bids
      pre: runBid() processing must be completed
      """
      params = Params(params).default("detail", 0)
      params[self.__class__.__name__] = self

      if (params["outputFormat"] == "html"):
         params.set("indent", 0)
         self.hashers.printResultByHasher(params)
      elif (params["outputFormat"] is None):
                                # hashers.hasher
         wantNoBid           = ((params["noBidHasher"]           or 0) != 0)
         wantSuccessfulBid   = ((params["successfulBidHasher"]   or 0) != 0)
         wantUnsuccessfulBid = ((params["unsuccessfulBidHasher"] or 0) != 0)

         if ((not (wantNoBid or wantSuccessfulBid or wantUnsuccessfulBid)) or
             (wantNoBid and wantSuccessfulBid and wantUnsuccessfulBid)):
            printHeading("/// results by hasher ///", 0, 1)
         elif (wantNoBid and (not wantSuccessfulBid  ) and
                             (not wantUnsuccessfulBid)):
            printHeading("/// hashers with no bids ///", 0, 1)
         else:
            headline = ""
            if (wantSuccessfulBid):
               headline += ", successful"
            if (wantUnsuccessfulBid):
               headline += ", unsuccessful"
            if (wantNoBid):
               headline += ", no bid"
            headline = re.sub("^, ", "", headline)
            headline = re.sub(", ([^,]*)$", ", and \\1", headline)
            printHeading("/// results by " + headline + " hasher ///", 0, 1)

         params.set([("indent"   , 0),
                     ("headLevel", 2)])
                                # detail: 0=bare; 1=show bid value
         self.hashers.printResultByHasher(params)
      else:
         sys.stderr.write(selfName                           +
                          ": TrailBid.printResultByTrail():" +
                          " unknown output format: "         +
                          params["outputFormat"] + "\n")

###########################################################################

   def printResultByNoBidHasher(self, params = Params()):
      """
      use: Wrapper for printResultByHasher() to print only hashers
           who have submitted no bids
      """
      self.printResultByHasher(Params([("noBidHasher", 1)]))

###########################################################################

   def printResultBySuccessfulHasher(self, params = Params()):
      """
      use: Wrapper for printResultByHasher() to print only hashers who
           have submitted at least one bid, but none of the submitted
           bids were successful
      """
      self.printResultByHasher(Params([("successfulBidHasher", 1)]))

###########################################################################

   def printResultByUnsuccessfulHasher(self, params = Params()):
      """
      use: Wrapper for printResultByHasher() to print only hashers with
           at least one successful bid
      """
      self.printResultByHasher(Params([("unsuccessfulBidHasher", 1)]))

###########################################################################

   def printResultByTrail(self, params = Params()):
      """
      use: For each time slot, print list of trails and the hashers with
           a successful bid for the trail
      pre: runBid() processing must be completed
      """
      params = Params(params).default("detail", 0)
      params[self.__class__.__name__] = self
                                # timeSlots.trails.trail.successfulBids.
                                # bid.hasher.print
      if (params["outputFormat"] in ("roster", "html")):
         self.timeSlots.printResultByTrail(params)
      elif (params["outputFormat"] is None):
         printHeading("/// results by trail ///", 0, 1)
         params.set([("indent"   , 0),
                     ("headLevel", 2)])
         self.timeSlots.printResultByTrail(params)
      else:
         sys.stderr.write(selfName                           +
                          ": TrailBid.printResultByTrail():" +
                          " unknown output format: "         +
                          params["outputFormat"] + "\n")

###########################################################################
###########################################################################
###########################################################################

def explain(hasherId):
   """
   use: Explains what happened to a hasher's bid(s)
   usage: Pass hasherID
   pre: runBid() processing must be completed
   """
   trailBid.hashers.getById(int(hasherId)).explain()

def help(verbosity = 0):
   print("explain(hasherID)   explain a hasher's bids")
   print("help(verbosity = 0) help")
   if (verbosity > 0):
      print()
      print("Top-level methods:")
      print("  trailBid.printResult(detail = 0)")
      print("  trailBid.printResultByHasher(params = Params())")
      print("  trailBid.printResultByNoBidHasher(params = Params())")
      print("  trailBid.printResultBySuccessfulHasher(params = Params())")
      print("  trailBid.printResultByTrail(params = Params())")
      print("  trailBid.printResultByUnsuccessfulHasher(params = Params())")
#       for method in [attribute for attribute in dir(TrailBid)
#                                if callable(getattr(TrailBid, attribute)) and
#                                   attribute.startswith('__') is False]:
#          print("trailBid." + method)

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
                       eventDirectory + "\n")
      exit(1)

   printHeading("/// settings ///", 0, 1)
   settings["eventDirectory"] = eventDirectory
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
         print(timeSlot.pretty())
         timeSlot.getBids().sortEquitably().printBids(
                                               Params([("indent"   , 0),
                                                       ("headLevel", 2),
                                                       ("detail"   , 1)]))

###########################################################################

   print()
                                # pass detail=1 to show hasher bid value
   trailBid.printResultByTrail()
   trailBid.printResultByTrail(Params("outputFormat", "html"  ))
   trailBid.printResultByTrail(Params("outputFormat", "roster"))

   print()
   trailBid.printResultByHasher(Params("detail", 1))
   trailBid.printResultByHasher(Params("outputFormat", "html"))

#    print()
#    trailBid.printResultBySuccessfulHasher()

   print()
   trailBid.printResultByUnsuccessfulHasher()

   print()
   trailBid.printResultByNoBidHasher()

###########################################################################
