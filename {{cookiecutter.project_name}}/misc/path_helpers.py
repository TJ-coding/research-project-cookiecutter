import yaml
from typing import List, Tuple
from pathlib import Path

# Custom YAML representer for None values
def represent_none(self, _):
    return self.represent_scalar('tag:yaml.org,2002:null', '')

yaml.add_representer(type(None), represent_none)

# Load paths.yaml file
def load_paths_yaml() -> dict:
    with open('paths.yaml', 'r') as handle:
        return yaml.load(handle, Loader=yaml.FullLoader)
    
def save_paths_yaml(paths: dict):
    with open('paths.yaml', 'w') as handle:
        yaml.dump(paths, handle)

# Convert a tree structure to a list of paths and custom names
def tree_to_list(tree: dict, current_path: Path) -> Tuple[List[Path], List[None|str]]:
    paths = []
    custom_names = []
    stack = [(tree[x], current_path) for x in tree.keys()]
    
    while stack:
        sub_tree, current_path = stack.pop()
        custom_names.append(sub_tree.get('custom_name'))
        paths.append(current_path)
        
        for key, value in sub_tree.items():
            if key == 'custom_name':
                continue
            if isinstance(value, dict):
                stack.append((value, current_path / key))
            else:
                custom_names.append(None)
                paths.append(current_path / key)
    
    return paths, custom_names

# Convert a list of paths and custom names back to a tree structure
def list_to_tree(data_dir_file_paths: List[Path], custom_names: List[None|str]) -> dict:
    root = {'Data': {}}
    path_data = list(zip(data_dir_file_paths, custom_names))
    
    for path, custom_name in path_data:
        path_parts = path.parts
        current = root
        
        for part in path_parts:
            if part == 'custom_name':
                raise ValueError('custom_name is a reserved key')
            current = current.setdefault(part, {})
        
        if custom_name is not None:
            current['custom_name'] = custom_name

    # Replace empty dictionaries with None
    def replace_empty_dict_with_none(current):
        if not current:
            return None
        for key in current:
            if isinstance(current[key], dict):
                current[key] = replace_empty_dict_with_none(current[key])
        return current

    return replace_empty_dict_with_none(root)
