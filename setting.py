# name: $Id: setting.py 6 15:02:09 04-Mar-2022 s01rz $

import re

from resource import *

###########################################################################

class Settings:
   """
   use: Class for preference settings
   imp: Store key-value pairs based on case-insensitive keys
   """
   def __init__(self, settingsFilespec = None):
      self.dict   = {} # dictionary of keys:values pairs
      self.lookup = {} # case-insensitive dictionary for the actual key
      if ((settingsFilespec is not None) and
          (settingsFilespec != ''      )):
         self.readFile(settingsFilespec)

###################################

   def __getitem__(self, key):
      return(self.dict[self.lookup[key.lower()]] if key.lower() in self.lookup
                                                 else None)

###################################

   def __setitem__(self, key, value):
      self.lookup[key.lower()] = key
      self.dict[key]           = value

###########################################################################

   def setDefault(self, key, value):
      """
      use: Set a key's value if the key does not exist; if the key exists,
           then nothing is done
      """
      self[key] = self[key] or value

###########################################################################

   def readFile(self, settingsFilespec = None):
      if (settingsFilespec is None):
         settingsFilespec = "settings.txt"
      elif (os.path.isdir(settingsFilespec)):
         settingsFilespec = os.path.join(settingsFilespec,
                                         "settings.txt")
      for line in open(settingsFilespec, 'r').readlines():
         if (re.match('^ *[^#;]+=', line) is not None):
            tokens = line.split('=')
            if len(tokens) >= 2:
               key       = tokens[0].strip()
               value     = '='.join(tokens[1:]).strip()
               self[key] = value

###########################################################################

                                # instantiate blank object
settings = Settings()
