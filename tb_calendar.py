# name: $Id: tb_calendar.py 2 01:29:41 18-May-2021 rudyz $

"""
use: calendar is a procedure, not a class. calendar reads a calendar input
     file and joins trails to time slots
"""

import csv
import sys

import timeSlot
import trail

from resource import *
from setting  import *

###########################################################################

def calendar(filespec, timeSlots, trails):
   """
   calendar is not a class; it is a plain procedure tying trails to time
   slots. A time slot is when one or more trails occur; a trail can belong
   to exactly one time slot
   """
   if (os.path.isdir(filespec)):
      filespec = os.path.join(filespec, "calendar.txt")

   with open(filespec, "r") as csvfile:
      events     = 0
      lineNumber = 0
      csvReader  = csv.reader(csvfile)
      if (csv.Sniffer().has_header(open(csvfile.name).read(1024))):
         lineNumber += 1
         next(csvReader)
      for row in csvReader:
         events     += 1
         lineNumber += 1
         if (len(row) != 0):
            timeSlot    = timeSlots.getById(row[0].strip())
            trail       = trails.getById(str(row[1]).strip())
            if ((timeSlot is None) or
                (trail    is None)):
                                # carve out for lineNumber 1 where timeSlot
                                # and trail are both None is probably a
                                # header that the csv.Sniffer failed to detect
               if (not ((lineNumber == 1 ) and
                        (timeSlot is None) and
                        (trail    is None))):
                  printFileReadError(lineNumber,
                                     str(timeSlot) + " -> " + str(trail))
            else:
               if (settings["verbosity"] != 0):
                  print(str(timeSlot) + " -> " + str(trail))
               try:
                  timeSlot.addTrail(trail)
                  trail.timeSlot= timeSlot
               except Exception as exception:
                  writeFileReadError(filename  ,
                                     lineNumber,
                                     exception ,
                                     str(timeSlot)   + " -> " + str(trail))
                  print("*** Line " + str(lineNumber) + " *** " +
                        row[0] + ", " + row[1])
                  raise
      if (settings["verbosity"] == 0):
         print(str(events)             + " " +
               plural(events, "event") + " " +
               "connected to time "          +
               plural(events, "slot"))
