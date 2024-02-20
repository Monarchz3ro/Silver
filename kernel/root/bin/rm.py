# rm - remove files and directories
# Usage: rm [-r] file1 file2 file3...
# Removes the provided files and directories.

def main(self:object, args: list[str]):
    if len(args) == 0 or "--h" in args:
        self.cout("///USAGE///\nrm <-r> (file) <file2> <file3>...\nRemoves the provided files and directories.")
        return
    flags = []; paths = []
    for arg in args:
        if arg.startswith("-"):
            flags.append(arg)
        else:
            paths.append(arg)
    try:
        for path in paths:
            self.remove(path, r="-r" in flags)
    except Exception as e:
        self.cout(f"///ERROR///\n{e}")