# whoami - print effective userid
# Usage: whoami
# echoes the effective userid to the console.

def main(self:object, args: list[str]):
    if len(args) == 0 or "--h" in args:
        print("///USAGE///\nwhoami\nechoes the effective userid to the console.")
        return
    elif self.whoami() == "root":
        print("---SYSTEM ADMIN PRIVILEGES DETECTED---")
    print(self.whoami())
    return