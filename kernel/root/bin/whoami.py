# whoami - print effective userid
# Usage: whoami
# echoes the effective userid to the console.

def main(self:object, args: list[str]):
    if "--h" in args or len(args) > 0:
        print("///USAGE///\nwhoami\nechoes the effective userid to the console.")
        return
    elif self.whoami() == "root":
        print("---YOU ARE THE ADMINISTRATOR OF THIS SYSTEM---")
        return
    print(self.whoami())
    return
