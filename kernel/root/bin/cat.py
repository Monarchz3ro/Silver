# to be plugged into the Terminal class
# cat - concatenate and print files
# syntax: cat [file1] [file2]... - print the contents of the specified files
# syntax: cat > [file] - concatenate the contents of the specified files and write the result to file
# syntax: cat [file1] [file2]... > [file3] - concatenate the contents of the specified files and write the result to file3
# syntax: cat [file1] [file2]... >> [file3] - concatenate the contents of the specified files and append the result to file3

def main(self:object, args:list[str]):
    if len(args) == 0 or "--h" in args:
        self.cout("///USAGE///\ncat file1 file2... > file3\nPrints the contents of the specified files to the terminal.")
        return
    writes = []; paths = []
    for spam,eggs in enumerate(args):
        if eggs in [">", ">>"]:
            writes.append(spam)
            user_input = []
            # get user input until there's a line break
            print('---USER INPUT---')
            while True:
                try:
                    line = input()
                except EOFError:
                    break
                user_input.append(line)
            print('---USER INPUT---')
        else:
            paths.append(eggs)
    
    # if there are no writes, print the contents of the files
    if writes == []:
        for path in paths:
            try:
                self.print_file(path.replace("\\", "/"))
            except Exception as e:
                print(f"///ERROR///\n{e}")

    
    # if there are writes, concatenate the files and write the result to the specified file
    else:
        if len(writes) > 1:
            self.cout("Cannot write to more than one file at a time.")
            return
        if (len(args)-1) in writes:
            self.cout("No file to write to.")
            return
        
        if ">" in args:
            concat = args[:writes[0]] # get the files to concatenate
            content = user_input
            count = 0
            try:
                for path in concat:
                    try:
                        content += self.read_file(path)
                    except Exception as e:
                        self.cout(f"///ERROR///\n{e}")
                while count < len(content):
                    self.append_file(args[writes[0] + 1], content[count] + "\n")
                    count += 1
                print("---SUCCESS---\nFile written successfully.")
            except ValueError as e:
                self.cout(f"///ERROR///\n{e}")

        elif ">>" in args:
            concat = args[:writes[0]]
            content = user_input
            count = 0
            try:
                for path in concat:
                    try:
                        content += self.read_file(path)
                    except ValueError as e:
                        self.cout(f"///ERROR///\n{e}")
                while count < len(content):
                    self.append_file(args[writes[0] + 1], content[count] + "\n")
                    count += 1
                print("---SUCCESS---\nFile appended successfully.")
            except ValueError as e:
                self.cout(f"///ERROR///\n{e}")
        else:
            self.cout("Invalid write operation.")