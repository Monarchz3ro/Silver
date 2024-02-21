# whoami - print effective userid
# Usage: whoami
# echoes the effective userid to the console.

def main(self:object, args: list[str]):
    if "--h" in args or len(args) > 0:
        self.cout("///USAGE///\nwhoami\nechoes the effective userid to the console.")
        return
    elif self.whoami() == "root":
        self.cout("---YOU ARE THE ADMINISTRATOR OF THIS SYSTEM---")
        return
    self.cout(self.whoami())
    return
