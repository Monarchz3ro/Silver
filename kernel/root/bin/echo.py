# echo - echoes arguments
# Usage: echo [arg1] [arg2] [arg3]...
# echoes the provided arguments to the console.

def main(self:object, args: list[str]):
    if len(args) == 0 or "--h" in args:
        print("///USAGE///\necho \"the world is whatever i want it to be!\"...\nechoes the provided arguments to the console.")
        return
    # check if there's environment variables and
    # replace them by their value instead
    output = " ".join(args)
    for i in list(self.shell_variables):
        output = output.replace(i, str(self.shell_variables[i]))
    print(output)
    return