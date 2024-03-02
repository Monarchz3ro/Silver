#to be plugged into the Terminal class
#cd - change directory
#syntax: cd [directory] - change to the specified directory

def main(self:object, args:list[str]):
    if len(args) == 0 or "--h" in args:
        self.cout("///USAGE///\ncd dir")
        return
    target = args[0]
    is_a_dir = self.isdir(target)
    if not is_a_dir:
        self.cout(f"///ERRORS///\n'{target}' isn't a directory")
    else:
        try:
            self.change_directory(target)
        except ValueError as e:
            self.cout(f"///ERROR///\n{e}")