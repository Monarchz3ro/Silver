# to be plugged into the Terminal class
# userdel - delete an existing user
# syntax: userdel <group>:<user> - delete an user entry

def main(self:object, args:list[str]):
    if len(args) < 1 or "--h" in args:
        self.cout("///USAGE///\nuserdel <group>:<user>\nDelete an user entry.")
        return
    try:
        user_to_delete = args[0].split(":", 1)[1]
    except:
        user_to_delete = args[0]
    try:
        user_group = args[0].split(":", 1)[0]
    except:
        self.remove_user_entry(user_to_delete)
        return
    self.remove_user_entry(user_to_delete, user_group)
