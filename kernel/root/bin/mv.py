import os
import shutil

# move an item into a new location

def main(self:object, args: list[str]):
    if len(args) < 2 or "--h" in args:
        self.cout("///USAGE///\nmv <current location> <new location>")
        return
    else:
        # check if first location exists
        item = os.path.join(self.current_directory, args[0])
        new_location = os.path.join(self.current_directory, args[1])
        try:
            if not os.path.exists(item):
                self.cout(f"///ERROR///\nitem '{item}' does not exist")
            else:
                shutil.move(item, new_location)
        except Exception as error:
            self.cout(f"///ERROR///\n{error}")
