# touch - change file timestamps
# Usage: touch file1 file2 file3...
# Changes the access and modification times of the provided files.

def main(self: object, args: list[str]):
    if len(args) == 0 or "--h" in args:
        print(
            "///USAGE///\ntouch (file) <file2> <file3>...\nChanges the access and modification times of the provided files.")
        return
    for path in args:
        try:
            self.touch(path)
        except Exception as e:
            print(f"///ERROR///\n{e}")
