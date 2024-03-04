# to be plugged into the Terminal class
# useradd - create a new user
# syntax: useradd <group>:<user> - create a new user entry

def main(self:object, args:list[str]):
    if len(args) < 1 or "--h" in args:
        self.cout("///USAGE///\nuseradd <group>:<user>\nCreate a new user entry.")
        return
    user_to_create = args[0].split(":", 1)[1]
    try:
        user_group = args[0].split(":", 1)[0]
    except:
        self.add_user_entry(user_to_create)
        return
    self.add_user_entry(user_to_create, user_group)
