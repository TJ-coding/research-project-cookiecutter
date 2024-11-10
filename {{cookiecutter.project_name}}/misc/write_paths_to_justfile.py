from typing import List, NamedTuple, Set
from pathlib import Path
from path_helpers import load_paths_yaml, tree_to_list
import re

class PathToVariableNameConverter:
    def __init__(self, used_variable_names: Set[str] = None):
        if used_variable_names is None:
            used_variable_names = set()
        self.used_variable_names = used_variable_names
        self.allowed_first_chars = set('abcdefghijklmnopqrstuvwxyz_')

    @staticmethod
    def camel_case_to_snake_case(camel_case: str) -> str:
        snake_case = camel_case[0].lower()
        for i in range(1, len(camel_case)):
            if camel_case[i].isupper() and (camel_case[i-1].islower() or (i+1 < len(camel_case) and camel_case[i+1].islower())):
                snake_case += '_'
            snake_case += camel_case[i].lower()
        return snake_case

    def convert(self, path: str) -> str:
        path_parts = list(Path(path).parts)
        suffix = '_dir' if Path(path).is_dir() else '_file'
        var_name = ''
        while path_parts:
            part = path_parts.pop()
            var_name = self.camel_case_to_snake_case(Path(part).stem) + (f'_{var_name}' if var_name else '')
            if var_name[0] not in self.allowed_first_chars:
                var_name = f'_{var_name}'
            if var_name + suffix not in self.used_variable_names:
                break
        var_name += suffix
        self.used_variable_names.add(var_name)
        return var_name

class StackItem(NamedTuple):
    current_dict: dict
    current_path: Path
    parent_var_name: str
    parent_path: Path

def make_justfile_path_expressions(path_yaml: dict, paths: List[Path], path_names: List[str]) -> List[str]:
    path_to_name = {str(path): name for path, name in zip(paths, path_names)}
    stack = [StackItem(path_yaml['Data'], Path('Data'), 'path_of_this_file', Path(''))]
    expressions = ['path_of_this_file := justfile_directory()']

    while stack:
        item = stack.pop()
        current_dict, current_path, parent_var_name, parent_path = item
        if current_path.is_dir():
            expressions.append("")
            expressions.append(f'{"#"*len(current_path.parts)} {path_to_name[str(current_path)].replace("_dir", "").replace("_", " ").upper()} PATHS')
        expressions.append(f'{path_to_name[str(current_path)]} := {parent_var_name} + "/{current_path.relative_to(parent_path)}"')
        if current_dict is None:
            continue
        for key, value in current_dict.items():
            if key != 'custom_name':
                stack.append(StackItem(value, current_path / key, path_to_name[str(current_path)], current_path))
    return expressions

def write_justfile_path_expressions_to_justfile(justfile_expressions: List[str]):    
    with open('Justfile', 'r') as handle:
        justfile_text: str = handle.read()
    
    prefix = '# == FILE PATHS == [Auto Generated DO NOT TOUCH!!!]'
    suffix = '# ==== [Auto Generated DO NOT TOUCH!!!]'
    prefix_regex = prefix.replace('[', '\[').replace(']', '\]')
    suffix_regex = suffix.replace('[', '\[').replace(']', '\]')
    match = re.search(f'{prefix_regex}([\s\S]*?){suffix_regex}', justfile_text)
    
    if match is None:
        justfile_text = f'{prefix}\n' + '\n'.join(justfile_expressions) + f'\n{suffix}\n\n' + justfile_text
    else:
        justfile_text = justfile_text.replace(match.group(0), f'{prefix}\n' + '\n'.join(justfile_expressions) + f'\n{suffix}')
    
    with open('Justfile', 'w') as handle:
        handle.write(justfile_text)
    

if __name__ == '__main__':
    paths_yaml = load_paths_yaml()
    if paths_yaml is None:
        paths, path_names = [], []
    else:
        paths, path_names = tree_to_list(paths_yaml, Path('Data'))

    converter = PathToVariableNameConverter(set(path_names))
    for i, (path, name) in enumerate(zip(paths, path_names)):
        if name is None:
            path_names[i] = converter.convert(path)

    justfile_expressions: List[str] = make_justfile_path_expressions(paths_yaml, paths, path_names)
    write_justfile_path_expressions_to_justfile(justfile_expressions)

