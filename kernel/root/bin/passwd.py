# to be plugged into the Terminal class
# passwd - change the password of an entry
# syntax: passwd <group>:<user> - change an user entry password

def main(self:object, args:list[str]):
    if "--h" in args:
        self.cout("///USAGE///\npasswd <group>:<user>\nChange an user entry password.")
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
