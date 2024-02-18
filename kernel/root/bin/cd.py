# to be plugged into the Terminal class
# cd - change directory
# syntax: cd [directory] - change to the specified directory
import os


def main(self: object, args: list[str]):
    if len(args) == 0 or "--h" in args:
        self.cout("///USAGE///\ncd dir")
        return
    target = os.path.normpath(os.path.join(self.current_directory, args[0]))
    try:
        self.change_directory(target)
    except ValueError as e:
        print(f"///ERROR///\n{e}")
