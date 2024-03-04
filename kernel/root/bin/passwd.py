# to be plugged into the Terminal class
# userdel - delete an existing user
# syntax: userdel <group>:<user> - delete an user entry

def main(self:object, args:list[str]):
    if "--h" in args:
        self.cout("///USAGE///\nuserdel <group>:<user>\nDelete an user entry.")
        return
    if len(args) == 0:
        user, group = self.get_working_entry()
        self.change_password(user, group)
    else:
        single_entry = False
        try:
            user = args[0].split(":", 1)[1]
        except:
            user = args[0]
            single_entry = True
        if not single_entry:
            group = args[0].split(":", 1)[0]
            self.change_password(user, group)
            return
        self.change_password(user)
