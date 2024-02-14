#to be plugged into the Terminal class
#cd - change directory
#syntax: cd [directory] - change to the specified directory

import os

def main(self:object, args:list[str]):
    self.cout("CD TRIGGERED.\n Passed in args: " + str(args) + "\n")
    if len(args) != 1 or "--h" in args:
        self.cout("Usage: cd <directory_name>")
        return
    target = os.path.normpath(os.path.join(self.current_directory, args[1]))
    if self.validated(target):
        self.current_directory = target
        return
    if not self.allowed(target, "r"):
        self.cout("///ERROR: PERMISSION DENIED///\nYou do not have permission to access this directory.")
        return
    self.cout(f"Directory not found: {'Attempted to escape root' if target.lstrip(self.clipout) == '' else target.lstrip(self.clipout)}")
