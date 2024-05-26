import os
import ast
import sys

def find_dependencies(file):
  with open(file, 'r') as f:
    tree = ast.parse(f.read(), file)
  abs_dependencies = []
  rel_dependencies = []
  for node in ast.walk(tree):
    if isinstance(node, ast.Import):
      for alias in node.names:
        # find that file and parse it
        abs_dependencies.append(alias.name)
    elif isinstance(node, ast.ImportFrom):
      for name in node.names:
        mod = "" if node.module == None else node.module
        if node.level == 0:
          abs_dependencies.append((mod, name.name))
        else:
          rel_dependencies.append((node.level, (mod, name.name)))

  return abs_dependencies, rel_dependencies

def std_lib(library):
  return library in sys.stdlib_module_names

def find_file(f, project_root, mod_name):
  file_name = os.path.join(project_root, f.replace('.', '/') + '.py')
  if os.path.exists(file_name):
    return file_name
  file_name = os.path.join(project_root, f.replace('.', '/'), mod_name + '.py')
  if os.path.exists(file_name):
    return file_name
  file_name = os.path.join(project_root, f.replace('.', '/'), '__init__.py')
  if os.path.exists(file_name):
    return file_name
  print("Not Found: ", file_name, file=sys.stderr)
  return None

def abs_library_gatherer(abs_dep, project_root):
  files_to_import = []
  for dep in abs_dep:
    if isinstance(dep, tuple):
      if std_lib(dep[0]):
        print("Standard Library: ", dep, file=sys.stderr)
      else:
        f = find_file(dep[0], project_root, dep[1])
        if f:
          files_to_import.append(f)
    else:
      if std_lib(dep):
        print("Standard Library: ", dep, file=sys.stderr)
      else:
        f = find_file(dep, project_root, dep)
        if f:
          files_to_import.append(f)
  return files_to_import

def rel_library_gatherer(rel_dep, file_path):
  files_to_import = []
  for dep in rel_dep:
    level = os.path.join(file_path, (dep[0] - 1) * '../')
    file_name = dep[1][0].replace('.', '/')
    f = find_file(file_name, level, dep[1][1])
    if f != None:
      files_to_import.append(f)
  return files_to_import

if __name__ == '__main__':
  file = sys.argv[1]
  file_root = os.path.dirname(file)
  project_root = sys.argv[2]
  DEP_helper = find_dependencies(file)
  python_std_library_list = sys.stdlib_module_names
  dependecies = abs_library_gatherer(DEP_helper[0], project_root) + rel_library_gatherer(DEP_helper[1], file_root)
  d = {}
  while True:
    c = 0
    res = []
    for dep in dependecies:
      if dep in d:
        continue
      d[dep] = True
      c = 1
      DEP_helper = find_dependencies(dep)
      abs_dep_ = abs_library_gatherer(DEP_helper[0], project_root)
      rel_dep_ = rel_library_gatherer(DEP_helper[1], os.path.dirname(dep))
      res += abs_dep_
      res += rel_dep_
    dependecies = list(set(dependecies + res))
    if c == 0:
      break
  print(dependecies)

def main_function(file, project_root):
  file_root = os.path.dirname(file)
  DEP_helper = find_dependencies(file)
  dependecies = abs_library_gatherer(DEP_helper[0], project_root) + rel_library_gatherer(DEP_helper[1], file_root)
  d = {}
  while True:
    c = 0
    res = []
    for dep in dependecies:
      if dep in d:
        continue
      d[dep] = True
      c = 1
      DEP_helper = find_dependencies(dep)
      abs_dep_ = abs_library_gatherer(DEP_helper[0], project_root)
      rel_dep_ = rel_library_gatherer(DEP_helper[1], os.path.dirname(dep))
      res += abs_dep_
      res += rel_dep_
    dependecies = list(set(dependecies + res))
    if c == 0:
      break
  return dependecies