import shutil, json, os
import importlib.util
from dataclasses import dataclass, field

######## refactored form of the original code ---version 0.0.2 ########
@dataclass
class Terminal:
    user:str = "root"
    kernel:str = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
    current_directory = root_dir = os.path.join(kernel,"root").replace("\\", "/")
    registry:str = "registry.json"
    filesystem:str = "ecosystem.json"
    current_time:str = "13 Feb 2024"
    clipout: str = kernel
    env_path_var:str = (os.path.join(root_dir,"bin")).replace("\\", "/")
    commands: dict = field(default_factory=dict)

    def __post_init__(self):
        self.load_commands()
        os.chdir(self.kernel)
        self.cout(f"Current System Directory: {os.getcwd()}")
        self.cout(f"Clipout: {self.clipout}")
        self.cout(f"Welcome to PathOS, {self.user}!")
        self.initialise()

    
    def load_commands(self):
        'load all commands from the bin directory.'
        for file in os.listdir(self.env_path_var):
            if file.endswith(".py"):
                module = file[:-3]
                try: ###this shit took me HOURS to fix - do NOT touch this
                    spec = importlib.util.spec_from_file_location(module, f"{self.env_path_var}/{file}")
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                except Exception as e:
                    print(f"Error processing command {file}: {e}")


        print(self.commands)

    def execute_command(self, command, args):
        if command in self.commands:
            to_execute = self.commands[command]
            to_execute(self, args)
        else:
            print(f'Unknown command: {command}')
    
    def cout(self, message, endl="\n"):
        print(message.replace("\\","/"), end=endl)

    def initialise(self):
        'initialise the system.'
        while True:
            to_strip = len(self.clipout)
            dir_prompt:str = f"{self.user}@PathOS:{self.current_directory[to_strip:]}~$ "
            self.cout(dir_prompt,endl="")
            comm = input()
            self.cout("Received command: " + comm)
            if not comm:
                continue
            comslist = comm.split()
            command = comslist[0]
            args = comslist[1:]
            self.execute_command(command, args)

    ###all of these are kernel methods - required for the system to function properly - do not mess with these
    ###unless you know what you are doing
    def get_registry(self):
        'get the registry of the system.'
        with open(self.registry, "r") as file:
            return json.load(file)
        
    def get_users(self):
        'get the users of the system.'
        return self.get_registry()["users"]

    def checkxistence(self, path):
        'check if a file or directory exists. accepts a relpath string.'
        return os.path.exists(os.path.join(self.root_dir, path))
    
    def legal(self, filepath=str):
        """Clamp to root. accepts a relpath string. Check if the specified path is within the root_dir. the path doesn't
        need to point to an existing path, just check if it's valid."""
        return os.path.commonpath([os.path.abspath(filepath), self.root_dir]) == self.root_dir

    def validated(self, filepath=str):
        """check if the specified exists AND is within the root_dir."""
        return self.checkxistence(filepath) and self.legal(filepath)
    
    def allowed(self, filepath, action, user, groups):
        'check if the user is allowed to perform the action on the path.'
        with open("metainf.json", "r") as meta:
            data = json.load(meta)
        if user == "root":
            return 1
        # Check if the path exists in the data
        if filepath in data:
            # Get the owner and group of the file
            owner = data[filepath]["owner"]
            group = data[filepath]["group"]
            permissions = data[filepath]["permissions"]
            # Check if the user is the owner
            if user == owner:
                if action in permissions[1:4]:
                    return 1
            # Check if the user is in the group
            for group_name in groups:
                if user in groups[group_name]:
                    if action in permissions[4:7]:
                        return 1
            # Check if the user is not the owner and not in the group
            else:
                if action in permissions[7:]:
                    return 1
        else:
            # If the path does not exist, reject request
            return 0  # returning 0 instead of False because i'm too used to return 0 from c++)
        return 0
        
    def sprint_through(self):
        "standalone tool to build the ecosystem.json file completely, assuming it doesn't exist in the first place or is empty."
        if not os.path.exists(self.filesystem):
            with open(self.filesystem, "w") as file:
                json.dump({}, file, indent=4)
    

        for filepath, dirs, files in os.walk(self.root_dir):
            for file in files:
                fullpath = os.path.join(filepath, file) # get the full path of the file
                relative_path = os.path.relpath(fullpath, self.root_dir) # get the relative path of the file
                self.create_new_meta_entry(
                    path_to_entry=relative_path.replace("\\", "/"),
                    permissions="drwxr-xr-x",
                    owner="root",
                    group="root",
                    size=os.path.getsize(fullpath),
                    last_modified=self.current_time,
                    name=file
                    )
    
            for dir in dirs:
                path = os.path.join(filepath, dir)
                relative_path = os.path.relpath(path, self.root_dir)
                self.create_new_meta_entry(
                    path_to_entry=relative_path.replace("\\", "/"),
                    permissions="drwxr-xr-x",
                    owner="root",
                    group="root",
                    size=0,
                    last_modified=self.current_time,
                    name=dir
                    )
                
    def create_new_meta_entry(self, path_to_entry, permissions, owner, group, size, last_modified, name):
        'create a new entry in the filesystem json file. the file must not exist before calling this method.'
        with open(self.filesystem, "r") as file:
            meta = json.load(file)
        data = {
            "permissions": permissions,
            "owner": owner,
            "group": group,
            "size": size,
            "last_modified": last_modified,
            "name": name,
        }
        meta[path_to_entry] = data
        with open(self.filesystem, "w") as file:
            json.dump(meta, file, indent=4)

    def update_meta_entry(self, path_to_entry, attribute, new_value):
        'update an attribute of an existing entry in the filesystem json file.'
        with open(self.filesystem, "r") as file:
            meta = json.load(file)
        meta[path_to_entry][attribute] = new_value
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
        return meta[path_to_entry]
    
    def cwd_to_relpath(self, path):
        absolute = os.path.normpath(os.path.join(self.current_directory, path))
        print("absolute", absolute)
        pathos_format = absolute[len(self.root_dir):].replace("\\", "/")
        return pathos_format

    ### end of kernel methods - system methods start here

    def create_new_file(self, path_to_file, data:dict=None, contents=""):
        'create a new file. accepts a relpath string, a parsed dict with metadata and a string of contents.'
        with open(os.path.join(self.root_dir, path_to_file), "w") as file:
            file.write(contents)
        self.create_new_meta_entry(*data)
    
    def create_new_directory(self, path_to_directory, data:dict=None):
        'create a new directory. accepts a relpath string and a parsed dict containing metadata.'
        os.makedirs(os.path.join(self.root_dir, path_to_directory))
        self.create_new_meta_entry(*data)
    
    def delete_file(self, path_to_file):
        'delete a file. accepts a relpath string.'
        os.remove(os.path.join(self.root_dir, path_to_file))
        self.delete_meta_entry(path_to_file)
    
    def delete_directory(self, path_to_directory):
        'delete a directory fully, ignoring if it had anything in it. accepts a relpath string.'
        shutil.rmtree(os.path.join(self.root_dir, path_to_directory))
        self.delete_meta_entry(path_to_directory)
    
    def general_move(self, path_to_file, new_path):
        'moves anything. accepts two relpath strings.'
        shutil.move(os.path.join(self.root_dir, path_to_file), os.path.join(self.root_dir, new_path))
        self.update_path_in_meta(path_to_file, new_path)
        self.update_meta_entry(new_path, "last_modified", self.current_time)
        self.update_meta_entry(new_path, "name", os.path.basename(new_path))
    
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
        with open(os.path.join(self.root_dir, path_to_file), "r") as file:
            return file.read()

    def set_file_contents(self, path_to_file, new_contents):
        'set the contents of a file. accepts a relpath string and a string of new contents.'
        with open(os.path.join(self.root_dir, path_to_file), "w") as file:
            file.write(new_contents)
        self.update_meta_entry(path_to_file, "last_modified", self.current_time)
    
    def get_directory_contents(self, path_to_directory):
        'get the contents of a directory. accepts a relpath string.'
        return os.listdir(os.path.join(self.root_dir, path_to_directory))
    
    ### end of system methods - os methods start here


terminal = Terminal()
