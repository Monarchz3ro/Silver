# mv - move files/rename them
# Usage: mv [-f] item new_location
# Move items(files or directories) across the system

def main(self:object, args:list[str]):
    if len(args) < 2 or "--h" in args:
        self.cout("///USAGE///\nmv <-f> (item) <new_location>\nMove items(files or directories) across the system.")
        return
    flags = []
    for arg in args:
        if arg.startswith("-"):
            flags.append(arg)
            args.remove(arg)
    item = args[0]
    new_location = args[1]
    if "-f" in flags:
        self.general_move(item, new_location, flags="-f" in flags)
    else:
        self.general_move(item, new_location)