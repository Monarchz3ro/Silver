#to be plugged into the Terminal class
#cd - change directory
#syntax: cd [directory] - change to the specified directory

import os

def main(self:object, args:list[str]):
    self.cout("CD TRIGGERED.\n Passed in args: " + str(args) + "\n")
    if len(args) == 0 or "--h" in args:
        self.cout("Usage: cd <directory_name>")
        return
    target = os.path.normpath(os.path.join(self.current_directory, args[0]))
    if self.validated(target):
        if not self.allowed(target, "r", self.user, self.groups):
            self.cout("///ERROR: PERMISSION DENIED///\nYou do not have permission to access this directory.")
            return
        self.current_directory = target
        return
    self.cout("///OPERATION FAILED///")