import shutil, json
import importlib.util
from dataclasses import dataclass, field
from datetime import date
from os import system, name
import os
import syscheck # custom
import tables # custom
import ast

######## refactored form of the original code ---version 0.0.3 ########

@dataclass
class Terminal:
    __def_user:str = "Monarch"
    __user:str = "Monarch"
    __groups: str = "users"
    __kernel:str = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
    __default_perms: str = "rwxr-x--x"
    __current_directory = __root_dir = os.path.join(__kernel,"root").replace("\\", "/")
    boot = os.path.join(__kernel, "root/boot/boot.bin").replace("\\", "/")
    __registry:str = "registry.json"
    filesystem:str = "ecosystem.json"
    current_date: str = date.today()
    current_formatted_data:str = current_date.strftime("%d %b %Y")
    clipout: str = __root_dir.replace("\\", "/")
    env_path_var:str = (os.path.join(__root_dir,"bin")).replace("\\", "/")
    commands: dict = field(default_factory=dict)
    shells: list = field(default_factory=list)
    shell_variables: dict = field(default_factory=dict)
    aliases: dict = field(default_factory=dict)

    # Get shell config
    if __groups == "root":
        shell_config: str = 'root/.silverrc'
    else:
        shell_config: str = f'home/{__user}/.silverrc'


    def __post_init__(self):
        self.boot_up()
        self.get_current_dir()
        self.create_default_environment_variables()
        self.load_shell_config()
        self.load_commands()
        os.chdir(self.__kernel)
        self.cout(f"PathOS is live and at your disposal.")
        self.initialise()


    def get_current_dir(self):
        # Get logical current directory depending
        # on the user name
        if self.__groups == "root":
            self.__current_directory = os.path.join(self.__kernel,"root/root").replace("\\", "/")
        else:
            self.__current_directory = os.path.join(self.__kernel,f"root/home/{self.__user}").replace("\\", "/")


    def boot_up(self):
        if self.checkxistence(self.boot):
            with open(self.boot, "r") as file:
                temp = file.read()
                if temp != syscheck.pathos_boot_module:
                    self.cout("///FATAL_CRASH.KERNEL.PANIC///\nBoot file is corrupted. Please reinstall the system.")
                    exit(1)
                self.cout("---BOOT SUCCESSFUL---")
        else:
            self.cout("///BOOTLOADER UNDISCOVERED///\nThe boot.bin file is missing from the /boot directory. Please reinstall the system.")
            exit(1)

    def create_default_environment_variables(self):
        self.shell_variables["$PATH"] = self.env_path_var
        self.shell_variables["$DATE"] = self.current_date
        self.shell_variables["$PRETTY_DATE"] = self.current_formatted_data
        self.shell_variables["$REGISTRY"] = self.__registry
        self.shell_variables["$FILESYSTEM"] = self.filesystem
        self.shell_variables["$BOOT"] = self.boot
        
            
    def load_shell_config(self):
        with open(os.path.join(self.__root_dir, self.shell_config)) as f:
            shell_config_raw = f.readlines()
            # load the lines one by one and check
            # if the line starts with a valid statement
            for i in shell_config_raw:
                if i.startswith('PATH='):  # if there's a binaries path definition
                    path = i.split("='", 1)[1].split("'", 1)[0]
                    self.env_path_var = (os.path.join(self.__root_dir, path)).replace("\\", "/")
                elif i.startswith('EXPORT '):  # if there's a environment variable export/creation
                    export_var_name = i.split('EXPORT ', 1)[1].split('=', 1)[0]
                    export_var_value = i.split("='", 1)[1].split("'", 1)[0]
                    self.shell_variables[export_var_name] = export_var_value
                elif i.startswith('alias '):  # if there's an alias export/creation
                    alias_name = i.split('alias ', 1)[1].split('=', 1)[0]
                    alias_command = i.split("='", 1)[1].split("'", 1)[0]
                    self.aliases[alias_name] = alias_command
    
    def __has_imports(self, module):
        try:
            with open(module.__file__, 'r') as f:
                module_content = f.read()
            tree = ast.parse(module_content)
        except SyntaxError:
            self.cout(f"Error parsing {module.__name__}. Skipping.")
            return False

        # check if the AST contains any import statements
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom): 
                return True

        return False

    def clear_prompt(self):
        # for windows
        if name == 'nt':
            _ = system('cls')
    
        # for mac and linux(here, os.name is 'posix')
        else:
            _ = system('clear')

    def execute_alias(self, alias_name):
        command = ""
        args = []
        str_args = ""
        to_print = ""
        count = 0
        while count < len(list(self.aliases[alias_name])):
            to_print = to_print + list(self.aliases[alias_name])[count]
            if to_print in self.commands:
                command = to_print
                str_args = self.aliases[alias_name].split(command, 1)[1]

            count += 1

        args_str = str_args.split(' -', 1)[1]
        args += ['-' + str_args.split(' -', 1)[1]]
        for i in range(str_args.count(' -') - 1):
            args_str = '-' + args_str.split(' -', 1)[1]
            args += [args_str]
        
        self.execute_command(command, args)

    def load_commands(self):
        'load all commands from the bin directory.'
        for file in os.listdir(self.env_path_var):
            if file.endswith(".py"):
                module = file[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(module, f"{self.env_path_var}/{file}")
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if self.__has_imports(mod):
                        self.cout(f"!!!FATAL ERROR!!!\n{module} module contains import statements.\nSkipping to minimize risks of system compromise.")
                        continue
                    if hasattr(mod, "main") and callable(mod.main):
                        self.commands[module] = mod.main
                    else:
                        self.cout(f"Error: {module} module does not have a 'main' function.")
                except Exception as e:
                    self.cout(f"Error processing command {file}: {e}")

    def execute_command(self, command, args):
        'execute a command.'
        if command == "su":
            self.__process_su(args)
        elif command in self.commands:
            if self.allowed(f"root/bin/{command}.py", 'x', self.__user, self.__groups):
                to_execute = self.commands[command]
                try:
                    to_execute(self, args)
                except AttributeError as err:
                    print(f"///FATAL ERROR///\nmodule '{command}' is using unauthorized locked-down kernel variables")
            else:
                print(f"Silver: cannot execute command '{command}' --> Permission denied.")
        else:
            try:
                self.execute_alias(command)
            except:
                self.cout(f'Silver: command "{command}" not found.')
    
    def cout(self, message, endl="\n"):
        self.cout(message.replace("\\","/"), end=endl)

    def initialise(self):
        'initialise the system.'
        while True:
            to_strip = len(self.clipout)
            dir_prompt:str = f"{self.__user.lower()}@PathOS:{self.__current_directory[to_strip:].lower()}/ $ "
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
            elif command in ["exit","logout","quit"]:
                if self.shells:
                    self.__pathos_bus_shell_out()
                    continue
            self.execute_command(command, args)

    ###all of these are __kernel methods - required for the system to function properly - do not mess with these
    ###unless you know what you are doing

    def __process_sudo(self, args):
        'process the sudo command.'
        target_user = self.__user
        target_group = self.__groups
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
            if self.__user == "root":
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
            if self.__user == "root":
                self.cout("///ERROR///\nYou are already the system administrator.")
                return
            if self.__pass_authenticated(self.__get_user_pass(self.__user, self.__groups)):
                self.cout(f"---AUTHENTICATION SUCCESSFUL---")
            else:
                self.cout("///ERROR///\nAuthentication failed.")
                return
            target_user = "root"
            target_group = "root"
            

        if retain_shell: # if the -s flag was present, perform actions in a shell
            index = args.index("-s")
            args.pop(index)
        
        command_mode = len(args) > 0 # if there are any args left, it means that there is a command, and it is to be executed in a shell
        if command_mode:
            command = args[0]
            args = args[1:]

            #from this point on, branch out to see if a simple switch is required
            #or if the command is to be executed in a shell

            if retain_shell: #shell out
                self.__pathos_bus_shell(target_user, target_group)
                self.execute_command(command, args)
            else: #simple switch
                store_user = self.__user
                store_group = self.__groups
                self.__user = target_user
                self.__groups = target_group
                ###sudo su branch
                if command == "su":
                    # args = args.insert(0, command) #insert the command back into the argslist so that it can be processed by the su method
                    success = self.__process_su(args)
                    if success != True: #if an error occurred, switch back to the original user
                        self.__user = store_user
                        self.__groups = store_group
                    return #do not switch back to the original user, as the su command will have changed the user
                else: #execute normally, because there is no su
                    self.execute_command(command, args)
                    self.__user = store_user
                    self.__groups = store_group
        else:
            if retain_shell: #shell out
                self.__pathos_bus_shell(target_user, target_group)

    def __process_su(self, args):
        shell_retain = "-" in args
        command_mode = "-c" in args
        authorised = self.__user == "root"
        target_user = "root" #default
        target_group = "root" #default

        if shell_retain: #remove the - flag from the argslist
            index = args.index("-")
            args.pop(index)
        
        if command_mode: #remove the -c flag and the command from the argslist
            index = args.index("-c")
            commandslist = args[index+1:]
            command = commandslist[0]
            args_to_pass = commandslist[1:]
            args.pop(index)
            args = args[:index]     
        
        #args is now the target user because every other option was cleaned from the argslist. if there is no args, the target user is root
        if args: #handle the user
            try:
                target_user = args[0]
                target_group = self.__pathos_bus_locate_user_in_group(target_user)
            except ValueError as e:
                self.cout(f"///ERROR///\n{e}")
                return
        
        if not authorised: #skip the password check if the user is already root
            if self.__pass_authenticated(self.__get_user_pass(target_user, target_group)):
                self.cout(f"---AUTHENTICATION SUCCESSFUL---")
                authorised = 1
            else:
                self.cout("///ERROR///\nAuthentication failed.")
                return
        
        if shell_retain: #shell out
            self.__pathos_bus_shell(target_user, target_group)
            if command_mode:
                self.execute_command(command, args_to_pass)
            return True
        else: #simple switch
            self.__user = target_user
            self.__groups = target_group
            if "-p" not in args:
                self.get_current_dir()
            if command_mode:
                self.execute_command(command, args_to_pass)
            return True 

    def __pathos_bus_locate_user_in_group(self, user):
        'locate the user in the group.'
        if user == "root":
            return "root"
        with open(self.__registry, "r") as file:
            reg_object = json.load(file)
        for group in reg_object["groups"]:
            if user in reg_object["groups"][group]:
                return group
        raise ValueError("Failed to locate user in group.")
    
    def __pass_authenticated(self, password):
        'ask for the password and authenticate the user.'
        self.cout("Password: ", endl="")
        passw = input()
        if passw == password:
            return 1
        return 0

    
    def __pathos_bus_shell(self, target_user, target_group, user_memory=__user ,group_memory=__groups,suppress=False):
        'start a new shell.'
        self.shells.append([user_memory,group_memory,self.__current_directory])
        self.__user = target_user
        self.__groups = target_group
        if not suppress:
            self.cout(f"---SHELL ACTIVE---\n{self.__user} is now active.")
    
    def __pathos_bus_shell_out(self, suppress=False):
        'exit the current shell.'
        dump = self.shells.pop()
        self.__user = dump[0]
        self.__groups = dump[1]
        self.__current_directory = dump[2]
        if not suppress:
            self.cout(f"{self.__user} is now active.")
            
    def __get_root_pass(self):
        'get the root password.'
        with open(self.__registry, "r") as file:
            reg_object = json.load(file)
            return reg_object["root"]["password"]
        
    def __get_user_pass(self, user, group):
        'get the user password.'
        if user == "root" and group == "root":
            return self.__get_root_pass()
        with open(self.__registry, "r") as file:
            reg_object = json.load(file)
        return reg_object["groups"][group][user]["password"]
    
    def get_registry(self):
        'get the registry of the system.'
        with open(self.__registry, "r") as file:
            return json.load(file)
        
    def get_users(self):
        'get the users of the system.'
        return self.get_registry()["users"]

    def checkxistence(self, path):
        'check if a file or directory exists. accepts a relpath string.'
        ret = os.path.exists(os.path.join(self.__root_dir, path))
        if not ret:
            self.cout(f"Path given does not exist.")
        return ret
    
    def legal(self, filepath=str):
        """Clamp to root. accepts a relpath string. Check if the specified path is within the root_dir. the path doesn't
        need to point to an existing path, just check if it's valid."""
        ret = os.path.commonpath([os.path.abspath(filepath), self.__root_dir]).replace("\\","/") == self.__root_dir
        if not ret:
            self.cout(f"///SECURITY ERROR///\n3: Virtualisation Breakthrough Suppressed.")
        return ret

    def validated(self, filepath=str):
        """check if the specified exists AND is within the root_dir."""
        ret = self.checkxistence(filepath) and self.legal(filepath)
        return ret
        
    def allowed(self, filepath, action, user, __groups):
        'check if the user is allowed to perform the action on the path.'
        filepath = os.path.relpath(filepath, self.__kernel).replace("\\", "/")
        if user == "root":
            return 1
        with open(self.filesystem, "r") as meta:
            data = json.load(meta)
        # Check if the path exists in the data
        if filepath in data:
            # Get the owner and group of the file
            owner = data[filepath]["owner"]
            __groups = data[filepath]["group"]
            permissions = data[filepath]["permissions"]

            #get the perms of the file
            with open(self.__registry, "r") as file:
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
                last_modified=self.current_formatted_data,
                name="root"
            )
        for filepath, dirs, files in os.walk(self.__root_dir):
            for file in files:
                fullpath = os.path.join(filepath, file) # get the full path of the file
                relative_path = os.path.relpath(fullpath, self.__kernel) # get the relative path of the file
                self.create_new_meta_entry(
                    path_to_entry=relative_path.replace("\\", "/"),
                    permissions="-rwxr-x--x",
                    owner=self.__user,
                    group=self.__groups,
                    size=os.path.getsize(fullpath),
                    last_modified=self.current_formatted_data,
                    name=file
                    )
    
            for dir in dirs:
                path = os.path.join(filepath, dir)
                relative_path = os.path.relpath(path, self.__kernel)
                self.create_new_meta_entry(
                    path_to_entry=relative_path.replace("\\", "/"),
                    permissions="drwxr-xr-x",
                    owner=self.__user,
                    group=self.__groups,
                    size=0,
                    last_modified=self.current_formatted_data,
                    name=dir
                    )
                
    def detect_new_dirs(self):
        'detect new directories and add them to the filesystem json file.'
        with open(self.filesystem, "r") as file:
            meta = json.load(file)
        for filepath, dirs, _ in os.walk(self.__root_dir):
            for dir in dirs:
                path = os.path.join(filepath, dir)
                relative_path = os.path.relpath(path, self.__kernel).replace("\\", "/")
                if relative_path not in meta:
                    self.create_new_meta_entry(
                        path_to_entry=relative_path.replace("\\", "/"),
                        permissions="drwxr-xr-x",
                        owner=self.__user,
                        group=self.__groups,
                        size=0,
                        last_modified=self.current_formatted_data,
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
        meta[os.path.relpath(path_to_entry,self.__kernel).replace("\\","/")][attribute] = new_value
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
        return meta[('root/' + path_to_entry.replace("\\","/")).replace('root/root/', 'root/')]
        
    def get_ecosystem_data(self):
        with open(self.filesystem, "r") as file:
            meta = json.load(file)
            
        # check for every items in the ecosystem
        # if the user has read permission to it
        for i in list(meta):
            if not self.allowed(os.path.join(self.__kernel, i), "r", self.__user, self.__groups):
                meta.pop(i)
        return meta

    ### end of kernel methods - system methods start here

    def create_new_file(self, path_to_file, data:dict=None, contents=""):
        'create a new file. accepts a relpath string, a parsed dict with metadata and a string of contents.'
        self.cout(os.path.join(self.__root_dir, path_to_file))
        with open(os.path.join(self.__root_dir, path_to_file), "w") as file:
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
        os.makedirs(os.path.join(self.__root_dir, path_to_directory))
        self.create_new_meta_entry(*data)
    
    def delete_file(self, path_to_file):
        'delete a file. accepts a relpath string.'
        os.remove(os.path.join(self.__current_directory, path_to_file))
        self.delete_meta_entry(path_to_file)
    
    def delete_directory(self, path_to_directory):
        'delete a directory fully, ignoring if it had anything in it. accepts a relpath string.'
        shutil.rmtree(os.path.join(self.__current_directory, path_to_directory))
        self.delete_meta_entry(path_to_directory)
    
    def general_move(self, path_to_file, new_path, flags=None):
        'moves anything. accepts two relpath strings.'
        if self.validated(os.path.join(self.__current_directory, path_to_file)):
            relative_path_to_file = os.path.join(self.__current_directory, path_to_file).split('kernel/', 1)[1]
            relative_new_path = os.path.join(self.__current_directory, new_path).split('kernel/', 1)[1]
            self.cout(relative_path_to_file, relative_new_path)
            self.update_path_in_meta(relative_path_to_file, relative_new_path)
            self.update_meta_entry(relative_new_path, "last_modified", self.current_formatted_data)
            self.update_meta_entry(relative_new_path, "name", os.path.basename(relative_new_path))
            shutil.move(os.path.join(self.__current_directory, path_to_file), os.path.join(self.__current_directory, new_path))
    
    def general_copy(self, path_to_file, new_path):
        'copies anything. accepts two relpath strings.'
        shutil.copy2(os.path.join(self.__root_dir, path_to_file), os.path.join(self.__root_dir, new_path))
        self.create_new_meta_entry(
            path_to_entry=new_path,
            permissions=self.get_meta_entry(path_to_file)["permissions"],
            owner=self.get_meta_entry(path_to_file)["owner"],
            group=self.get_meta_entry(path_to_file)["group"],
            size=self.get_meta_entry(path_to_file)["size"],
            last_modified=self.current_formatted_data,
            name=os.path.basename(new_path)
            )
    
    def get_file_contents(self, path_to_file):
        'get the contents of a file. accepts a relpath string.'
        with open(os.path.join(self.__current_directory, path_to_file).replace("\\","/"), "r") as file:
            return file.read()
    
    ## methods that expose the kernel to the bus
    
    def __pathos_bus_cd(self, path):
        'pathos bus method to expose the cd command to the bus. changes active directory of the current working system.'
        self.__current_directory = os.path.normpath(os.path.join(self.__current_directory, path))
    
    def __pathos_bus_listdir(self, path):
        'pathos bus method to expose the ls command to the bus.'
        return os.listdir(os.path.join(self.__root_dir, path))
    
    def __pathos_bus_is_root(self):
        if self.__groups == "root":
            return True
        return False
    
    def __pathos_bus_entry_exists(self, entry, group):
        with open(self.__registry, "r") as file:
            reg_object = json.load(file)
            if not group in list(reg_object["groups"]):
                return False
            elif not entry in list(reg_object["groups"][group]):
                return False
        return True
    
    def __pathos_bus_add_entry(self, entry, group):
        'pathos bus method to create a new user entry'
        with open(self.__registry, "r") as file:
            reg_object = json.load(file)
            if not group in list(reg_object["groups"]):  # if the group doesn't exists, create it
                reg_object["groups"][group] = {}
            reg_object["groups"][group][entry] = {}  # create the user entry
            passwd = input(f"Password for {entry}: ")
            reg_object["groups"][group][entry]["password"] = passwd  # create the user password
        with open(self.__registry, "w") as file:
            reg_object = json.dump(reg_object, file, indent=4)

    def __pathos_bus_remove_entry(self, entry, group):
        'pathos bus method to remove an user entry'
        with open(self.__registry, "r") as file:
            reg_object = json.load(file)
            del reg_object["groups"][group][entry]
        with open(self.__registry, "w") as file:
            reg_object = json.dump(reg_object, file, indent=4)

    def __pathos_bus_listdir_long(self, path):
        'pathos bus method to expose ls -l to the bus'
        files = os.listdir(os.path.join(self.__root_dir, path))
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
        os.mkdir(os.path.join(self.__current_directory, path))
    
    def __pathos_bus_mkdir_p(self, path):
        'pathos bus method to expose the mkdir -p command to the bus.'
        os.makedirs(os.path.join(self.__current_directory, path))

    def __pathos_bus_update_meta(self, path_to_entry, attribute, new_value):
        'pathos bus method to expose the ecosystem to the bus.'
        with open(self.filesystem, "r") as file:
            meta = json.load(file)
        meta[os.path.relpath(path_to_entry,self.__kernel).replace("\\","/")][attribute] = new_value
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
        meta[os.path.relpath(path_to_entry,self.__kernel).replace("\\","/")] = data
        with open(self.filesystem, "w") as file:
            json.dump(meta, file, indent=4)
    
    def __pathos_bus_remove(self, path, r=False):
        'pathos bus method to expose the rm command to the bus.'
        path = os.path.relpath(os.path.join(self.__current_directory, path), self.__kernel).replace("\\","/")
        if not r:
            try:
                os.remove(os.path.join(self.__kernel,path))
                self.delete_meta_entry(path)
                self.cout(f"---SUCCESS---\n{os.path.basename(path)} removed.")
            except Exception as e:
                self.cout("///ERROR///\nInvalid input for provided args.\n"+str(e))
        else: # (if r)
            with open(self.filesystem, "r") as file:
                memory_dump = json.load(file)
            try:
                for filepath, drs, files in os.walk(os.path.join(self.__current_directory, path)):
                    for file in files:
                        self.delete_meta_entry(os.path.relpath(os.path.join(filepath, file), self.__kernel).replace("\\","/"))
                    for dr in drs:
                        self.delete_meta_entry(os.path.relpath(os.path.join(filepath, dir), self.__kernel).replace("\\","/"))
                shutil.rmtree(os.path.join(self.__kernel,path))
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
        target = os.path.normpath(os.path.join(self.__current_directory, path)).replace("\\","/")
        if self.validated(target):
            if not self.allowed(target, "x", self.__user, self.__groups):
                raise ValueError("1: Forbidden Route")
            self.__pathos_bus_cd(path)
            return
        raise ValueError("2: Validation Check Failed")
        
    def add_user_entry(self, entry, group="users"):
        'scripting method to create a new user entry'
        if not self.__pathos_bus_is_root():
            self.cout(f"///ERROR///\nDon't have permission to create user entry '{group}:{entry}'.")
        elif self.__pathos_bus_entry_exists(entry, group):
            self.cout(f"///ERROR///\nEntry '{group}:{entry}' already exists.")
        else:
            self.__pathos_bus_add_entry(entry, group)
    
    def remove_user_entry(self, entry, group="users"):
        'scripting method to delete an user entry'
        if not self.__pathos_bus_is_root():
            self.cout(f"///ERROR///\nDon't have permission to delete user entry '{group}:{entry}'.")
        elif not self.__pathos_bus_entry_exists(entry, group):
            self.cout(f"///ERROR///\nEntry '{group}:{entry}' doesn't exists.")
        else:
            self.__pathos_bus_remove_entry(entry, group)
    
    def list_directory(self, path, long=False):
        'scripting method to list directories'
        target = os.path.normpath(os.path.join(self.__root_dir, path)).replace("\\","/")
        if self.validated(target):
            if not self.allowed(target, "x", self.__user, self.__groups):
                raise ValueError("1: Forbidden Route")
            elif long:
                return self.__pathos_bus_listdir_long(path)
            return self.__pathos_bus_listdir(path)
        raise ValueError("2: Validation Check Failed")
    
    def list_current_directory(self, long=False):
        return self.list_directory(self.__current_directory, long)
    
    def make_directory(self, path, p=False):
        'scripting method to make directories'
        target = os.path.normpath(os.path.join(self.__current_directory, path)).replace("\\","/")
        parent_to_target = os.path.dirname(target)
        if self.legal(target):
            if not self.allowed(parent_to_target, "w", self.__user, self.__groups):
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
        target = os.path.normpath(os.path.join(self.__current_directory, path)).replace("\\","/")
        if self.validated(target):
            if not self.allowed(target, "r", self.__user, self.__groups):
                raise ValueError("1: Forbidden Route")
            to_print = self.get_file_contents(path)
            self.cout(to_print)
            return
        raise ValueError("2: Validation Check Failed")
    
    def write_file(self, path, contents):
        'scripting method to write to a file'
        target = os.path.normpath(os.path.join(self.__current_directory, path)).replace("\\","/")
        if not self.checkxistence(target):
            self.cout("A new one shall be created.")
            parent_to_target = os.path.dirname(target)
            if not self.allowed(parent_to_target, "w", self.__user, self.__groups):
                raise ValueError("1: Forbidden Route")
            elif not self.legal(target):
                raise ValueError("3: Virtualisation Breakthrough Suppressed")
            data = {
                "permissions":f"-{self.default_perms}",
                "owner":self.__user,
                "group":self.__groups,
                "size":self.get_size(contents),
                "last_modified":self.current_formatted_data,
                "name": os.path.basename(target)
                }
            with open(os.path.join(self.__current_directory, path), "w") as file:
                file.write(contents)
            self.__pathos_bus_add_meta(target, data["permissions"], data["owner"], data["group"], data["size"], data["last_modified"])
            return
        
        elif self.validated(target):
            if not self.allowed(target, "w", self.__user, self.__groups):
                raise ValueError("1: Forbidden Route")
            with open(os.path.join(self.__current_directory, path), "w") as file:
                file.write(contents)
            self.__pathos_bus_update_meta(target, "last_modified", self.current_formatted_data)
            self.__pathos_bus_update_meta(target, "size", self.get_size(contents))
            return
        raise ValueError("2: Validation Check Failed")
    
    def append_file(self, path, contents):
        'scripting method to append to a file'
        target = os.path.normpath(os.path.join(self.__current_directory, path)).replace("\\","/")
        if self.validated(target):
            if not self.allowed(target, "w", self.__user, self.__groups):
                raise ValueError("1: Forbidden Route")
            with open(os.path.join(self.__current_directory, path), "a") as file:
                file.write(contents)
            self.__pathos_bus_update_meta(target, "last_modified", self.current_formatted_data)
            self.__pathos_bus_update_meta(target, "size", self.get_size(contents))
            return
        raise ValueError("2: Validation Check Failed")

    def read_file(self, path):
        'scripting method to read a file'
        target = os.path.normpath(os.path.join(self.__current_directory, path)).replace("\\","/")
        if self.validated(target):
            if not self.allowed(target, "r", self.__user, self.__groups):
                raise ValueError("1: Forbidden Route")
            return self.get_file_contents(path)
        raise ValueError("2: Validation Check Failed")
    
    def obtain_shells(self, listform = False):
        'scripting method to return active shells'
        active_shells = self.shells
        if not active_shells:
            raise ValueError("Misc: No shells detected.")
        ret = [f"{self.__def_user} (origin)" ]
        for shell in active_shells:
            ret.append(shell[0])
        if listform:
            ret.pop(0)
            return ret
        self.cout(" > ".join(ret))
    
    def ret_pwd(self):
        'scripting method to return the current working directory'
        cwd = self.__current_directory
        clip = len(self.clipout)
        return cwd[clip:].replace("\\","/")
    
    def ret_basename(self, path):
        'scripting method to return the basename of a path'
        return os.path.basename(path)
    
    def remove(self, path, r=False):
        'scripting method to remove a file'
        target = os.path.normpath(os.path.join(self.__current_directory, path)).replace("\\","/")
        if self.validated(target):
            if not self.allowed(target, "w", self.__user, self.__groups):
                raise ValueError("1: Forbidden Route")
            self.__pathos_bus_remove(path, r)
            return
        raise ValueError("2: Validation Check Failed")
    
    def touch(self, path):
        'scripting method to create a new file'
        target = os.path.normpath(os.path.join(self.__current_directory, path)).replace("\\","/")
        if not self.checkxistence(target):
            parent_to_target = os.path.dirname(target)
            if not self.allowed(parent_to_target, "w", self.__user, self.__groups):
                raise ValueError("1: Forbidden Route")
            elif not self.legal(target):
                raise ValueError("3: Virtualisation Breakthrough Suppressed")
            data = {
                "permissions":f"-{self.default_perms}",
                "owner":self.__user,
                "group":self.__groups,
                "size":0,
                "last_modified":self.current_formatted_data,
                "name": os.path.basename(target)
                }
            self.cout("It shall be created.")
            with open(os.path.join(self.__current_directory, path), "w") as file:
                file.write("")
            self.__pathos_bus_add_meta(target, data["permissions"], data["owner"], data["group"], data["size"], data["last_modified"])
            return
        else:
            self.update_meta_entry(target, "last_modified", self.current_formatted_data)
            self.cout(f"{os.path.basename(target)} touched.")
            return
    
    def whoami(self):
        'scripting method to return the current user'
        return self.__user
    
    def joinpath(self, *args):
        'scripting method to join paths'
        return os.path.join(*args).replace("\\","/")
    
    def isdir(self, path):
        'scripting method to check if a path is a directory'
        return os.path.isdir(os.path.join(self.__current_directory, path))
    
    def cout(self, message, endl="\n"):
        'scripting method to print to the terminal'
        if type(message) in [list, tuple]:
            for item in message:
                print(item.replace("\\","/"), end=endl)
            return
        elif type(message) == dict:
            for key in message:
                print(f"{key}: {message[key]}")
            return
        print(message.replace("\\","/"), end=endl)
    

    
terminal = Terminal()
