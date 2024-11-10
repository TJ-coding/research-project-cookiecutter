from pathlib import Path
from path_helpers import load_paths_yaml, tree_to_list, list_to_tree, save_paths_yaml

# Main execution
if __name__ == '__main__':
    current_paths_yaml = load_paths_yaml()
    if current_paths_yaml == None:
        current_paths, current_path_names = [], []
    else:
        current_paths, current_path_names = tree_to_list(current_paths_yaml, Path('Data'))
    current_paths_set = set(current_paths)
    
    data_dir_file_paths = list(Path('Data').rglob('*'))
    data_dir_file_paths = [path for path in data_dir_file_paths if path.stem[0] != '.']
    data_dir_file_paths = [path for path in data_dir_file_paths if path not in current_paths_set]
    
    new_paths_yaml = list_to_tree(data_dir_file_paths + current_paths, [None] * len(data_dir_file_paths) + current_path_names)
    
    save_paths_yaml(new_paths_yaml)