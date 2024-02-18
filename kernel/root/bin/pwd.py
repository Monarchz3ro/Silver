# to be plugged into the Terminal class
# pwd - print working directory
# syntax: pwd - print the current working directory

def main(self:object, args:list[str]):
    if len(args) > 0 or "--h" in args:
        self.cout("///USAGE///\npwd\nPrints the current working directory to the terminal.")
        return
    pwd = self.ret_pwd()
    if not pwd:
        self.cout("Working Dir: '/'")
        return
    self.cout(f"Working Dir: '{pwd}'")
