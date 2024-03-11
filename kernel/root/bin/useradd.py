# to be plugged into the Terminal class
# useradd - create a new user
# syntax: useradd <group>:<user> - create a new user entry

def main(self:object, args:list[str]):
    if len(args) < 1 or "--h" in args:
        self.cout("///USAGE///\nuseradd <group>:<user>\nCreate a new user entry.")
        return
    single_entry = False
    try:
        user_to_create = args[0].split(":", 1)[1]
    except:
        user_to_create = args[0]
        single_entry = True
    if not single_entry:
        user_group = args[0].split(":", 1)[0]
        self.add_user_entry(user_to_create, user_group)
        return
    self.add_user_entry(user_to_create)
