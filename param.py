# name: $Id: param.py 4 18:22:33 16-May-2021 rudyz $
"""
use: Generic object based construct for converting variable number of
     arguments in **kwargs into a Params object. Params objects gives us
     slighly more flexibility and allows us to define a __getitem__ that
     does not raise an exception if the key is not present in the
     dictionary
imp: Implemented as a wrapper, providing additional functionality methods,
     around a key-value pair dictionary
"""

import sys

###########################################################################
###########################################################################
###########################################################################
###
### p a r a m
###
###########################################################################
###########################################################################
###########################################################################

class Params:
   def __init__(self, kwargs, **defaultKWArgs):
      """
      use: A case-sensitive dictionary of key-value pairs that can be
           passed to functions, procedures, and method **kwargs
      usage: Typically:
                def foo(**kwargs):
                   params = Params(kwargs, default1 = defaultValue1,
                                           default2 = defaultValue2 ... )
      """
      self.args = self.defaultKWArgs(kwargs, **defaultKWArgs)

###################################

   def __call__(self, **kwargs):
      """
      use: This method has dual purposes.
           1. Simplifies a function, procedure, or method passing its
              Params(kwargs) to a child function by using **kwargs()
              instead of needing to know our internal layout
           2. Sets dictionary values from kwargs
      usage: For the former, typically, after construction as documented in
                __init__(), params is passed as:
                   childProcess(**params())
             For the latter:
                params(key1, value1,
                       key2, value2 ...)
      """
      if (len(kwargs) != 0):
         self.setValues(**kwargs)

      return(self.args)

###################################

   def __getitem__(self, key):
      return(self.args[key] if key in self.args else None)

###################################

   def __setitem__(self, key = None, value = None):
      self.args[key] = value
      return(self)

###################################

   def __str__(self):
      return(str(self.args))

###########################################################################

   def defaultKWArgs(cls, kwargs, **defaultKWArgs):
      """
      use: A class method to merge a pair of dicts, where kwargs values
           are augmented, but not overwritten, by values from defaultKWArgs
      post: A new dictionary will be returned
      """
      if (sys.version_info >= (3, 9)):
         return(defaultKWArgs | kwargs)
      elif (sys.version_info >= (3, 5)):
         return({**defaultKWArgs, **kwargs})
      else:
         for key, value in defaultKWArgs.items():
            if key not in kwargs:
               kwargs[key] = value
         return(kwargs)

###########################################################################

   def setKWArgs(cls, kwargs, **overridingKWargs):
      """
      use: A class method to merge a pair of dicts, where values in kwargs
           can be overwritten by values from overrdingKWArgs
      post: A new dictionary will be returned
      """
      if (sys.version_info >= (3, 9)):
         return(kwargs | overridingKWArgs)
      elif (sys.version_info >= (3, 5)):
         return({**kwargs, **overridingKWArgs})
      else:
         for key, value in overridingKWArgs.items():
            kwargs[key] = value
         return(kwargs)

###########################################################################

   def setDefaults(self, **kwargs):
      """
      use: Merge the kwargs dictionary into our dictionary, where kwargs
           values augments, but does not overwrite, values in our dictionary
      post: New values from kwargs that don't have an existing key in our
            dictionary will be inserted into our dictionary
      """
      for key, value in kwargs.items():
         if (key not in self.args):
            self.args[key] = value
      return(self)

###########################################################################

   def setValues(self, **kwargs):
      """
      use: Merge the kwargs dictionary into our dictionary, where kwargs
           values overwrites values in our dictionary
      post: Values from kwargs will be inserted into our dictionary
      """
      for key, value in kwargs.items():
         self.args[key] = value
      return(self)

###########################################################################
