# name: $Id: resource.py 3 20:31:50 08-Sep-2021 rudyz $

import os.path
import sys

selfName = os.path.basename(sys.argv[0])

###########################################################################

class AlreadyDoneError(Exception):
   pass

class DuplicateError(Exception):
   pass

class IncompleteObjectError(Exception):
   pass

###########################################################################

def printFileReadError(lineNumber, data):
   """
   use: Print nicely formatted error message during file reading
   """
   print(f"*** Line {str(lineNumber)} *** {data}")

###########################################################################

def printHeading(headline, indent = 0, headLevel = 0):
   """
   use: Print section headings or headlines with different levels of indent
        and highlighting/emphasis.
   """
   indentation        = "".ljust(0)
   underlineCharacter = ["#", "=", "-", "."]
   print(f"{indentation} {headline}")
   if ((headLevel >= 1) and (headLevel < len(underlineCharacter))):
      print(f"{indentation}"
            f" {underline_(headline, underlineCharacter[headLevel - 1])}")

###########################################################################

def underline_(string, underlineCharacter = "-"):
   """
   use: Return an underline suitable for underlining the passed string
   """
   return(f"{'':{underlineCharacter}>{len(string)}}")

def underline(string, underlineCharacter = "-"):
   """
   use: Print an underline for underlining the passed string
   """
   print(underline_(string, underlineCharacter))

def underlined(string, underlineCharacter = "-"):
   """
   use: Print the passed string, and the print its underline
   """
   print(string)
   underline(string, underlineCharacter)

###########################################################################

def plural(count, singular, multiple = None):
   """
   use: Pluralize word as required
   usage: Pass a numeric value for determining if the passed singular
          word needs to be pluralized. The singular word is pluralized
          by appending it with an "s". If the plural form of the
          singular word has an irregular plural form, it plural form can
          passed as an optional third argument
   """
   if (count == 1):
      return(singular)
   else:
      return(f"{singular}s" if multiple is None else multiple)

###########################################################################

def writeFileReadError(filename, lineNumber, exception, data):
   """
   use: Write a nicely formatted error message to stderr during file
        reading
   """
   sys.stderr.write(f"{selfName}: {filename} line {lineNumber}: "
                    f"{str(exception)}:\n"
                    f"  >>> {data}\n")

###########################################################################
