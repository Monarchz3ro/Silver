# locate - search for files in the database
# Usage: locate <occurrence string>
# Search for occurrences in files names.

def main(self:object, args: list[str]):
    if len(args) == 0 or "--h" in args:
        print("///USAGE///\nlocate <occurrence string>\nSearch for occurrences in files names.")
        return
    occurrence_string = args[0]
    list_of_files = []
    ecosystem = self.get_ecosystem_data()
    for item in list(ecosystem):
        if occurrence_string in item:
            list_of_files += [item]

    # format the list
    list_of_files = str(list_of_files)
    list_of_files = list_of_files.replace('[', '')
    list_of_files = list_of_files.replace(']', '')
    list_of_files = list_of_files.replace("'", '')
    list_of_files = list_of_files.replace(', ', '\n')
    print(list_of_files)

