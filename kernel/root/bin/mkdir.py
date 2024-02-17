# mkdir - make directories
# Usage: mkdir [-p] dir1 dir2 dir3...
# Creates new, empty directories with the provided arguments.

def main(self:object, args: list[str]):
    if len(args) == 0 or "--h" in args:
        print("///USAGE///\nmkdir <-p> (dir) <dir2> <dir3>...\nCreates new, empty directories with the provided arguments.")
        return
    flags = []; paths = []
    for arg in args:
        if arg.startswith("-"):
            flags.append(arg)
        else:
            paths.append(arg)
    try:
        for path in paths:
                self.make_directory(path, p="-p" in flags)
    except Exception as e:
        print(f"///ERROR///\n{e}")