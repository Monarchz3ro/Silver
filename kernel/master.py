import shutil, json, os
import importlib.util
from dataclasses import dataclass, field
import os
import syscheck
import tables

######## refactored form of the original code ---version 0.0.2 ########

@dataclass
class Terminal:
    user:str = "Monarch"
    groups: str = "users"
    kernel:str = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
    default_perms: str = "rwxr-xr-x"
    current_directory = root_dir = os.path.join(kernel,"root").replace("\\", "/")
    boot = os.path.join(kernel, "root/boot/boot.bin").replace("\\", "/")
    registry:str = "registry.json"
    filesystem:str = "ecosystem.json"
    current_time:str = "18 Feb 2024"
    clipout: str = root_dir.replace("\\", "/")
    env_path_var:str = (os.path.join(root_dir,"bin")).replace("\\", "/")
    commands: dict = field(default_factory=dict)
    shells: list = field(default_factory=list)

    def __post_init__(self):
        self.boot_up()
        self.load_commands()
        os.chdir(self.kernel)
        self.cout(f"PathOS is live and at your disposal.")
        self.initialise()

    def boot_up(self):
        if self.checkxistence(self.boot):
            with open(self.boot, "r") as file:
                temp = file.read()
                if temp != syscheck.pathos_boot_module:
                    self.cout("///FATAL_CRASH.KERNEL.PANIC///\nBoot file is corrupted. Please reinstall the system.")
                    exit(1)
                self.cout("---BOOT SUCCESSFUL---")
        else:
            self.cout("///BOOTLOADER UNDISCOVERED///\nThe boot.bin file is missing from the system directories. Please reinstall the system.")
            exit(1)

    def load_commands(self):
        'load all commands from the bin directory.'
        for file in os.listdir(self.env_path_var):
            if file.endswith(".py"):
                module = file[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(module, f"{self.env_path_var}/{file}")
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, "main") and callable(mod.main):
                        self.commands[module] = mod.main
                    else:
                        print(f"Error: {module} module does not have a 'main' function.")
                except Exception as e:
                    print(f"Error processing command {file}: {e}")

    def execute_command(self, command, args):
        if command in self.commands:
            to_execute = self.commands[command]
            to_execute(self, args)
        else:
            print(f'Silver: command "{command}" not found.')
    
    def cout(self, message, endl="\n"):
        print(message.replace("\\","/"), end=endl)

    def initialise(self):
        'initialise the system.'
        while True:
            to_strip = len(self.clipout)
            dir_prompt:str = f"{self.user.lower()}@PathOS:{self.current_directory[to_strip:].lower()}/ $ "
            self.cout(dir_prompt,endl="")
            comm = input()
            if not comm:
                continue
            comslist = comm.split()
            command = comslist[0]
            args = comslist[1:]
            if command == "sudo":
                self.__process_sudo(args)
                continue
            if command in ["exit","logout","quit"]:
                if self.shells:
                    self.__pathos_bus_shell_out()
                    continue
            self.execute_command(command, args)

    ###all of these are kernel methods - required for the system to function properly - do not mess with these
    ###unless you know what you are doing
            
    def __process_sudo(self, args):
        'process the sudo command.'
        target_user = self.user
        target_group = self.groups
        if not args:
            self.cout("///USAGE/// sudo [command] [args]")
            return
        
        user_specified = "-u" in args
        retain_shell = "-s" in args
        become_root = "-i" in args

        if user_specified:
            index = args.index("-u")
            target_user = args[index+1]
            target_group = self.__pathos_bus_locate_user_in_group(target_user)
            args.pop(index+1)
            args.pop(index)
            if self.__pass_authenticated(self.__get_user_pass(target_user, target_group)):
                self.cout(f"---AUTHENTICATION SUCCESSFUL---")
            else:
                self.cout("///ERROR///\nAuthentication failed.")
                return
        
        elif become_root:
            if self.user == "root":
                self.cout("///ERROR///\nYou are already the system administrator.")
                return
            if self.__pass_authenticated(self.__get_root_pass()):
                self.cout(f"---AUTHENTICATION SUCCESSFUL---")
            else:
                self.cout("///ERROR///\nAuthentication failed.")
                return
            target_user = "root"
            target_group = "root"
            index = args.index("-i")
            args.pop(index)

        else:
            if self.user == "root":
                self.cout("///ERROR///\nYou are already the system administrator.")
                return
            if self.__pass_authenticated(self.__get_user_pass(self.user, self.groups)):
                self.cout(f"---AUTHENTICATION SUCCESSFUL---")
            else:
                self.cout("///ERROR///\nAuthentication failed.")
                return
            target_user = "root"
            target_group = "root"
        
        if retain_shell: # remove the -s flag from the args
            index = args.index("-s")
            args.pop(index)
        
        self.__pathos_bus_shell(target_user, target_group, suppress=True)

        if args:
            command = args[0]
            args = args[1:]
            self.execute_command(command, args)

        if retain_shell: # if the -s flag was present, retain the shell
            self.cout(f"---SHELL ACTIVE---\n{self.user} is now active.")
            return
        self.__pathos_bus_shell_out(suppress=True)
        


    def __pathos_bus_locate_user_in_group(self, user):
        'locate the user in the group.'
        with open(self.registry, "r") as file:
            reg_object = json.load(file)
        for group in reg_object["groups"]:
            if user in reg_object["groups"][group]:
                return group
        raise  ValueError("Failed to locate user in group.")
    
    def __pass_authenticated(self, password):
        'ask for the password and authenticate the user.'
        self.cout("Password: ", endl="")
        passw = input()
        if passw == password:
            return 1
        return 0

    
    def __pathos_bus_shell(self, user, group, suppress=False):
        'start a new shell.'
        self.shells.append([self.user,self.groups,self.current_directory])
        self.user = user
        self.groups = group
        if not suppress:
            self.cout(f"---SHELL ACTIVE---\n{self.user} is now active.")
    
    def __pathos_bus_shell_out(self, suppress=False):
        'exit the current shell.'
        dump = self.shells.pop()
        self.user = dump[0]
        self.groups = dump[1]
        self.current_directory = dump[2]
        if not suppress:
            self.cout(f"{self.user} is now active.")
            
    def __get_root_pass(self):
        'get the root password.'
        with open(self.registry, "r") as file:
            reg_object = json.load(file)
            return reg_object["root"]["password"]
        
    def __get_user_pass(self, user, group):
        'get the user password.'
        with open(self.registry, "r") as file:
            reg_object = json.load(file)
        return reg_object["groups"][group][user]["password"]
    
    def get_registry(self):
        'get the registry of the system.'
        with open(self.registry, "r") as file:
            return json.load(file)
        
    def get_users(self):
        'get the users of the system.'
        return self.get_registry()["users"]

    def checkxistence(self, path):
        'check if a file or directory exists. accepts a relpath string.'
        ret = os.path.exists(os.path.join(self.root_dir, path))
        if not ret:
            self.cout(f"Path given does not exist.")
        return ret
    
    def legal(self, filepath=str):
        """Clamp to root. accepts a relpath string. Check if the specified path is within the root_dir. the path doesn't
        need to point to an existing path, just check if it's valid."""
        ret = os.path.commonpath([os.path.abspath(filepath), self.root_dir]).replace("\\","/") == self.root_dir
        if not ret:
            self.cout(f"///SECURITY ERROR///\n3: Virtualisation Breakthrough Suppressed.")
        return ret

    def validated(self, filepath=str):
        """check if the specified exists AND is within the root_dir."""
        ret = self.checkxistence(filepath) and self.legal(filepath)
        return ret
        
    def allowed(self, filepath, action, user, groups):
        'check if the user is allowed to perform the action on the path.'
        filepath = os.path.relpath(filepath, self.kernel).replace("\\", "/")
        if user == "root":
            return 1
        with open(self.filesystem, "r") as meta:
            data = json.load(meta)
        # Check if the path exists in the data
        if filepath in data:
            # Get the owner and group of the file
            owner = data[filepath]["owner"]
            groups = data[filepath]["group"]
            permissions = data[filepath]["permissions"]

            #get the perms of the file
            with open(self.registry, "r") as file:
                reg_object = json.load(file)
                grps = reg_object["groups"]
            # Check if the user is the owner
            if user == owner:
                if action in permissions[1:4]:
                    return 1
            # Check if the user is in the group
            for group_name in grps:
                if user in group_name:
                    if action in permissions[4:7]:
                        return 1
            # Check if the user is not the owner and not in the group
            else:
                if action in permissions[7:]:
                    return 1
        else:
            # If the path does not exist, reject request
            return 0  # returning 0 instead of False because i'm too used to return 0 from c++
        return 0
        
    def sprint_through(self):
        "standalone tool to build the ecosystem.json file completely, assuming it doesn't exist in the first place or is empty."
        if not os.path.exists(self.filesystem):
            with open(self.filesystem, "w") as file:
                json.dump({}, file, indent=4)
        self.create_new_meta_entry(
                path_to_entry="root",
                permissions="drwxr-xr-x",
                owner="root",
                group="root",
                size=0,
                last_modified=self.current_time,
                name="root"
            )
        for filepath, dirs, files in os.walk(self.root_dir):
            for file in files:
                fullpath = os.path.join(filepath, file) # get the full path of the file
                relative_path = os.path.relpath(fullpath, self.kernel) # get the relative path of the file
                self.create_new_meta_entry(
                    path_to_entry=relative_path.replace("\\", "/"),
                    permissions="drwxr-x--x",
                    owner=self.user,
                    group=self.groups,
                    size=os.path.getsize(fullpath),
                    last_modified=self.current_time,
                    name=file
                    )
    
            for dir in dirs:
                path = os.path.join(filepath, dir)
                relative_path = os.path.relpath(path, self.kernel)
                self.create_new_meta_entry(
                    path_to_entry=relative_path.replace("\\", "/"),
                    permissions="drwxr-xr-x",
                    owner=self.user,
                    group=self.groups,
                    size=0,
                    last_modified=self.current_time,
                    name=dir
                    )
                
    def detect_new_dirs(self):
        'detect new directories and add them to the filesystem json file.'
        with open(self.filesystem, "r") as file:
            meta = json.load(file)
        for filepath, dirs, _ in os.walk(self.root_dir):
            for dir in dirs:
                path = os.path.join(filepath, dir)
                relative_path = os.path.relpath(path, self.kernel).replace("\\", "/")
                if relative_path not in meta:
                    self.create_new_meta_entry(
                        path_to_entry=relative_path.replace("\\", "/"),
                        permissions="drwxr-xr-x",
                        owner=self.user,
                        group=self.groups,
                        size=0,
                        last_modified=self.current_time,
                        name=dir
                        )

    def create_new_meta_entry(self, path_to_entry, permissions, owner,group,size, last_modified, name):
        'create a new entry in the filesystem json file. the file must not exist before calling this method.'
        with open(self.filesystem, "r") as file:
            meta = json.load(file)
        data = {
            "permissions": permissions,
            "owner": owner,
            "group": group,
            "size": size,
            "last_modified": last_modified,
            "name": name
        }
        meta[path_to_entry] = data
        with open(self.filesystem, "w") as file:
            json.dump(meta, file, indent=4)

    def get_size(self, content:str):
        'returns size'
        return len(content.encode('utf-8'))

    def update_meta_entry(self, path_to_entry, attribute, new_value):
        'update an attribute of an existing entry in the filesystem json file.'
        with open(self.filesystem, "r") as file:
            meta = json.load(file)
        meta[os.path.relpath(path_to_entry,self.kernel).replace("\\","/")][attribute] = new_value
        with open(self.filesystem, "w") as file:
            json.dump(meta, file, indent=4)

    def delete_meta_entry(self, path_to_entry):
        'delete an entry from the filesystem json file.'
        with open(self.filesystem, "r") as file:
            meta = json.load(file)
        del meta[path_to_entry]
        with open(self.filesystem, "w") as file:
            json.dump(meta, file, indent=4)

    def update_path_in_meta(self, old_path, new_path):
        'update the path of an entry in the filesystem json file.'
        with open(self.filesystem, "r") as file:
            meta = json.load(file)
        meta[new_path] = meta.pop(old_path)
        with open(self.filesystem, "w") as file:
            json.dump(meta, file, indent=4)
    
    def get_meta_entry(self, path_to_entry):
        'get the metadata of an entry in the filesystem json file.'
        with open(self.filesystem, "r") as file:
            meta = json.load(file)
        return meta[path_to_entry.replace("\\","/")]

    ### end of kernel methods - system methods start here

    def create_new_file(self, path_to_file, data:dict=None, contents=""):
        'create a new file. accepts a relpath string, a parsed dict with metadata and a string of contents.'
        print(os.path.join(self.root_dir, path_to_file))
        with open(os.path.join(self.root_dir, path_to_file), "w") as file:
            file.write(contents)
        self.create_new_meta_entry(
                                    data["path_to_entry"],
                                    data["permissions"],
                                    data["owner"],
                                    data["group"],
                                    data["size"], 
                                    data["last_modified"],
                                    data["name"]
                                   )
    
    def create_new_directory(self, path_to_directory, data:dict=None):
        'create a new directory. accepts a relpath string and a parsed dict containing metadata.'
        os.makedirs(os.path.join(self.root_dir, path_to_directory))
        self.create_new_meta_entry(*data)
    
    def delete_file(self, path_to_file):
        'delete a file. accepts a relpath string.'
        os.remove(os.path.join(self.current_directory, path_to_file))
        self.delete_meta_entry(path_to_file)
    
    def delete_directory(self, path_to_directory):
        'delete a directory fully, ignoring if it had anything in it. accepts a relpath string.'
        shutil.rmtree(os.path.join(self.current_directory, path_to_directory))
        self.delete_meta_entry(path_to_directory)
    
    def general_move(self, path_to_file, new_path, flags=None):
        'moves anything. accepts two relpath strings.'
        if self.validated(os.path.join(self.current_directory, path_to_file)):
            relative_path_to_file = os.path.join(self.current_directory, path_to_file).split('kernel/', 1)[1]
            relative_new_path = os.path.join(self.current_directory, new_path).split('kernel/', 1)[1]
            print(relative_path_to_file, relative_new_path)
            self.update_path_in_meta(relative_path_to_file, relative_new_path)
            self.update_meta_entry(relative_new_path, "last_modified", self.current_time)
            self.update_meta_entry(relative_new_path, "name", os.path.basename(relative_new_path))
            shutil.move(os.path.join(self.current_directory, path_to_file), os.path.join(self.current_directory, new_path))
    
    def general_copy(self, path_to_file, new_path):
        'copies anything. accepts two relpath strings.'
        shutil.copy2(os.path.join(self.root_dir, path_to_file), os.path.join(self.root_dir, new_path))
        self.create_new_meta_entry(
            path_to_entry=new_path,
            permissions=self.get_meta_entry(path_to_file)["permissions"],
            owner=self.get_meta_entry(path_to_file)["owner"],
            group=self.get_meta_entry(path_to_file)["group"],
            size=self.get_meta_entry(path_to_file)["size"],
            last_modified=self.current_time,
            name=os.path.basename(new_path)
            )
    
    def get_file_contents(self, path_to_file):
        'get the contents of a file. accepts a relpath string.'
        with open(os.path.join(self.current_directory, path_to_file).replace("\\","/"), "r") as file:
            return file.read()
    
    ## methods that expose the kernel to the bus
    
    def __pathos_bus_cd(self, path):
        'pathos bus method to expose the cd command to the bus. changes active directory of the current working system.'
        self.current_directory = os.path.normpath(os.path.join(self.current_directory, path))
    
    def __pathos_bus_listdir(self, path):
        'pathos bus method to expose the ls command to the bus.'
        return os.listdir(os.path.join(self.root_dir, path))
    
    def __pathos_bus_listdir_long(self, path):
        'pathos bus method to expose ls -l to the bus'
        files = os.listdir(os.path.join(self.root_dir, path))
        result = []
        for file in files:
            item_path = os.path.relpath(os.path.join(path, file)).replace("\\","/")
            metadata = self.get_meta_entry(item_path)
            permissions = metadata["permissions"]
            owner = metadata["owner"]
            group = metadata["group"]
            size = metadata["size"]
            last_modified = metadata["last_modified"]
            name = metadata["name"]
            entry = [permissions, owner, group, size, last_modified, name]
            result.append(entry)
        return result
    
    def __pathos_bus_mkdir(self, path):
        'pathos bus method to expose the mkdir command to the bus.'
        os.mkdir(os.path.join(self.root_dir, path))
    
    def __pathos_bus_mkdir_p(self, path):
        'pathos bus method to expose the mkdir -p command to the bus.'
        os.makedirs(os.path.join(self.root_dir, path))

    def __pathos_bus_update_meta(self, path_to_entry, attribute, new_value):
        'pathos bus method to expose the ecosystem to the bus.'
        with open(self.filesystem, "r") as file:
            meta = json.load(file)
        meta[os.path.relpath(path_to_entry,self.kernel).replace("\\","/")][attribute] = new_value
        with open(self.filesystem, "w") as file:
            json.dump(meta, file, indent=4)
    
    def __pathos_bus_add_meta(self, path_to_entry, permissions, owner, group, size,last_modified):
        'pathos bus method to expose the ecosystem to the bus.'
        with open(self.filesystem, "r") as file:
            meta = json.load(file)
        data = {
            "permissions": permissions,
            "owner": owner,
            "group": group,
            "size": size,
            "last_modified": last_modified,
            "name": os.path.basename(path_to_entry)
        }
        meta[os.path.relpath(path_to_entry,self.kernel).replace("\\","/")] = data
        with open(self.filesystem, "w") as file:
            json.dump(meta, file, indent=4)
    
    def __pathos_bus_remove(self, path, r=False):
        'pathos bus method to expose the rm command to the bus.'
        path = os.path.relpath(os.path.join(self.current_directory, path), self.kernel).replace("\\","/")
        if not r:
            try:
                os.remove(os.path.join(self.kernel,path))
                self.delete_meta_entry(path)
                self.cout(f"---SUCCESS---\n{os.path.basename(path)} removed.")
            except Exception as e:
                self.cout("///ERROR///\nInvalid input for provided args.\n"+str(e))
        else: # (if r)
            with open(self.filesystem, "r") as file:
                memory_dump = json.load(file)
            try:
                for filepath, drs, files in os.walk(os.path.join(self.current_directory, path)):
                    for file in files:
                        self.delete_meta_entry(os.path.relpath(os.path.join(filepath, file), self.kernel).replace("\\","/"))
                    for dr in drs:
                        self.delete_meta_entry(os.path.relpath(os.path.join(filepath, dir), self.kernel).replace("\\","/"))
                shutil.rmtree(os.path.join(self.kernel,path))
                self.cout(f"---SUCCESS---\n{os.path.basename(path)} removed.")
                self.delete_meta_entry(path)
            except Exception as e:
                self.cout("///ERROR///\nInvalid input for provided args.\n"+str(e))
                with open(self.filesystem, "w") as file:
                    json.dump(memory_dump, file, indent=4)


    ## os methods - methods that serve the exposed kernel via the bus
    ## aka, "shit to use while scripting"

    def tabulate(self, table):
        tables.tabulate(table)

    def change_directory(self, path):
        'scripting method to change directories'
        target = os.path.normpath(os.path.join(self.current_directory, path)).replace("\\","/")
        if self.validated(target):
            if not self.allowed(target, "x", self.user, self.groups):
                raise ValueError("1: Forbidden Route")
            self.__pathos_bus_cd(path)
            return
        raise ValueError("2: Validation Check Failed")
    
    def list_directory(self, path, long=False):
        'scripting method to list directories'
        target = os.path.normpath(os.path.join(self.current_directory, path)).replace("\\","/")
        if self.validated(target):
            if not self.allowed(target, "x", self.user, self.groups):
                raise ValueError("1: Forbidden Route")
            elif long:
                return self.__pathos_bus_listdir_long(path)
            return self.__pathos_bus_listdir(path)
        raise ValueError("2: Validation Check Failed")
    
    def make_directory(self, path, p=False):
        'scripting method to make directories'
        target = os.path.normpath(os.path.join(self.current_directory, path)).replace("\\","/")
        parent_to_target = os.path.dirname(target)
        if self.legal(target):
            if not self.allowed(parent_to_target, "w", self.user, self.groups):
                raise ValueError("1: Forbidden Route")
            if p:
                self.__pathos_bus_mkdir_p(path) 
            else:
                self.__pathos_bus_mkdir(path)
            self.detect_new_dirs()
            return
        raise ValueError("3: Virtualisation Breakthrough Suppressed")
    
    def print_file(self, path):
        'scripting method to print contents of a file'
        target = os.path.normpath(os.path.join(self.current_directory, path)).replace("\\","/")
        if self.validated(target):
            if not self.allowed(target, "r", self.user, self.groups):
                raise ValueError("1: Forbidden Route")
            to_print = self.get_file_contents(path)
            self.cout(to_print)
            return
        raise ValueError("2: Validation Check Failed")
    
    def write_file(self, path, contents):
        'scripting method to write to a file'
        target = os.path.normpath(os.path.join(self.current_directory, path)).replace("\\","/")
        if not self.checkxistence(target):
            print("A new one shall be created.")
            parent_to_target = os.path.dirname(target)
            if not self.allowed(parent_to_target, "w", self.user, self.groups):
                raise ValueError("1: Forbidden Route")
            elif not self.legal(target):
                raise ValueError("3: Virtualisation Breakthrough Suppressed")
            data = {
                "permissions":f"-{self.default_perms}",
                "owner":self.user,
                "group":self.groups,
                "size":self.get_size(contents),
                "last_modified":self.current_time,
                "name": os.path.basename(target)
                }
            with open(os.path.join(self.current_directory, path), "w") as file:
                file.write(contents)
            self.__pathos_bus_add_meta(target, data["permissions"], data["owner"], data["group"], data["size"], data["last_modified"])
            return
        
        elif self.validated(target):
            if not self.allowed(target, "w", self.user, self.groups):
                raise ValueError("1: Forbidden Route")
            with open(os.path.join(self.current_directory, path), "w") as file:
                file.write(contents)
            self.__pathos_bus_update_meta(target, "last_modified", self.current_time)
            self.__pathos_bus_update_meta(target, "size", self.get_size(contents))
            return
        raise ValueError("2: Validation Check Failed")
    
    def append_file(self, path, contents):
        'scripting method to append to a file'
        target = os.path.normpath(os.path.join(self.current_directory, path)).replace("\\","/")
        if self.validated(target):
            if not self.allowed(target, "w", self.user, self.groups):
                raise ValueError("1: Forbidden Route")
            with open(os.path.join(self.current_directory, path), "a") as file:
                file.write(contents)
            self.__pathos_bus_update_meta(target, "last_modified", self.current_time)
            self.__pathos_bus_update_meta(target, "size", self.get_size(contents))
            return
        raise ValueError("2: Validation Check Failed")

    def read_file(self, path):
        'scripting method to read a file'
        target = os.path.normpath(os.path.join(self.current_directory, path)).replace("\\","/")
        if self.validated(target):
            if not self.allowed(target, "r", self.user, self.groups):
                raise ValueError("1: Forbidden Route")
            return self.get_file_contents(path)
        raise ValueError("2: Validation Check Failed")
    
    def ret_pwd(self):
        'scripting method to return the current working directory'
        cwd = self.current_directory
        clip = len(self.clipout)
        return cwd[clip:].replace("\\","/")
    
    def ret_basename(self, path):
        'scripting method to return the basename of a path'
        return os.path.basename(path)
    
    def remove(self, path, r=False):
        'scripting method to remove a file'
        target = os.path.normpath(os.path.join(self.current_directory, path)).replace("\\","/")
        if self.validated(target):
            if not self.allowed(target, "w", self.user, self.groups):
                raise ValueError("1: Forbidden Route")
            self.__pathos_bus_remove(path, r)
            return
        raise ValueError("2: Validation Check Failed")
    
    def touch(self, path):
        'scripting method to create a new file'
        target = os.path.normpath(os.path.join(self.current_directory, path)).replace("\\","/")
        if not self.checkxistence(target):
            parent_to_target = os.path.dirname(target)
            if not self.allowed(parent_to_target, "w", self.user, self.groups):
                raise ValueError("1: Forbidden Route")
            elif not self.legal(target):
                raise ValueError("3: Virtualisation Breakthrough Suppressed")
            data = {
                "permissions":f"-{self.default_perms}",
                "owner":self.user,
                "group":self.groups,
                "size":0,
                "last_modified":self.current_time,
                "name": os.path.basename(target)
                }
            self.cout("It shall be created.")
            with open(os.path.join(self.current_directory, path), "w") as file:
                file.write("")
            self.__pathos_bus_add_meta(target, data["permissions"], data["owner"], data["group"], data["size"], data["last_modified"])
            return
        else:
            self.update_meta_entry(target, "last_modified", self.current_time)
            self.cout(f"{os.path.basename(target)} touched.")
            return
    
    def whoami(self):
        'scripting method to return the current user'
        return self.user
    


terminal = Terminal()