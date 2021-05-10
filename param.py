# named: $Id: param.py 3 00:28:39 10-May-2021 rudyz $

"""
use: Generic object based construct for passing variable number of
     arguments instead of **kwargs. Params() gives us slighly more
     flexibility and allows constructs like:
        params[self.__class__.__name__] = self
     which we use to register the class name of each stack frame which
     allows called methods to locate a calling class object
usage: Although a Params() object is passed by value, data belonging to
       the params object is effectively passed by reference. If changes
       are intended to be made to the params values, the params objects
       should probably be shallow copied by the Params class's
       constructor behaving as a copy constructor by passing it an
       existting Params object
imp: Implemented as a key-value pair dictionary
"""

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
   def __init__(self, key = None, value = None):
      """
      use: A case-sensitive dictionary of key-value pairs that can be
           passed to functions, procedures, and methods varargs without
           involving **kwargs
      usage: In the simplest form, a blank Params object can be
             constructed with no arguments, otherwise, see set()
             method
      """
      self.list = {}
      self.set(key, value)

###################################

   def __getitem__(self, key):
      return(self.list[key] if key in self.list else None)

###################################

   def __setitem__(self, key = None, value = None):
      return(self.set(key, value))

###########################################################################

   def default(self, key, value = None):
      """
      use: Set a default value for a key
      imp: Will the passed key name to the passeod value if the key
           name is not aready in our dictionary
      """
      if (key is not None):
         if (isinstance(key, str)):
            if ((key not in self.list) and
                (value is not None)):
               self.set(key, value)
         else:
            for (k, v) in key:
               if ((k not in self.list) and
                   (v is not None)):
                  self.list[k] = v
      return(self)

###########################################################################

   def set(self, key = None, value = None):
      """
      use: Sets key-value pairs in our dictionary
      usage: A single key value can be set by passing a key and value.
             Multiple key-value pairs can get set by passing an array
             of two-element tuples consisting of a key and value.
             Finally another Params object can be passed in which case
             a shallow copy of the passed object will be made
      """
      if (key is not None):
         if (isinstance(key, str)):
            if (value is not None):
               self.list[key] = value
            elif (key in self.list):
               del(self.list[key])
         elif (isinstance(key, Params)):
            self.list = key.list.copy()
         else:
            for (k, v) in key:
               self.list[k] = v
      return(self)

###########################################################################
