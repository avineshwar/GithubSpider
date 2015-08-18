'''
Created on Aug 13, 2015

@author: Tommi Unruh
'''

import subprocess
import os
from time import sleep
import sys

class GitDownloader(object):
    """
    Manages the download of git repositories.
    """
    def __init__(self, dir_path):
        self.OUT_DIR = dir_path
    
        if self.OUT_DIR[-1] != "/":
            self.OUT_DIR += "/"
                
    def cloneAllFromFile(self, filename, linenumber=0):
        linenumber = int(linenumber)
        with open(filename, 'r') as fh:
            if linenumber > 1:
                self.goToLine(fh, linenumber)

            l = fh.readline()
            while l:
                try:
                    print "Trying link on line %d in file '%s'" % (linenumber, 
                                                                   filename)
                    self.cloneRepoLink(l.strip())
                
                except (
                    RepositoryExistsException, 
                    RepositoryDoesNotExistException
                    ) as err:
                        print str(err).strip()
                        print "Skipping..."
                    
                finally:
                    linenumber += 1
                    l = fh.readline()
                    
            print "End of file reached, my work is done!"
            
    def cloneRepoLink(self, link):
        msg     = "Cloning repository: %s..." % link
        out_dir = self.OUT_DIR + link[link.rfind("/") + 1 : -4]

        print "%s\r" % msg,
        sys.stdout.flush()
        process = subprocess.Popen(["git", "clone", link, out_dir], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if stderr:
            print "%s Failed." % msg
            if "already exists and is not an empty directory." in stderr:
                raise RepositoryExistsException(str(stderr))
            
            elif "does not exist" in stderr:
                raise RepositoryDoesNotExistException(str(stderr))
            
        print "%s Done." % msg
        
        if stdout:
            print stdout
    
    def goToLine(self, fh, linenumber):
        """
        Go to 'linenumber' of a huge text file in an (memory-)efficient way.
        """
        if linenumber < 1:
            raise IOError(
                "Specified linenumber '%d' is smaller than 1." % linenumber
                )
        
        fh.seek(0, os.SEEK_SET)

        # Skip lines until desired line is reached.
        for _ in range(0, linenumber - 1):
            read = fh.readline()
            if read == "":
                # Empty string represents EOF.
                raise OutOfScopeException(msg="goToLine error: ", 
                                          line=linenumber)
            

class RepositoryExistsException(BaseException):
    pass

class RepositoryDoesNotExistException(BaseException):
    pass

class OutOfScopeException(BaseException):
    def __init__(self, msg=None, line=None):
        if msg:
            self.message = msg
            
        if line:
            self.message += "Line %d is out of scope." % line
            
        else:
            self.message = (
                    "goToLine() was called with a linenumber, "
                    "which was out of scope."
                    )
        
    def __str__(self):
        return self.message