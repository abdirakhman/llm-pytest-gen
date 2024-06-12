import os
import sys
import ast
import json

import files_gatherer
import coverage_gatherer
import prompt_generation
import llm_chat


def open_file_and_number(file):
  with open(file, "r") as f:
    lines = f.readlines()
  numbered_lines = []
  for i, line in enumerate(lines):
    numbered_lines.append(f"{i+1}: {line}")
  return "".join(numbered_lines)

def open_file(file):
  with open(file, "r") as f:
    lines = f.readlines()
  return "".join(lines)

def parse_json(message):
  # find first line that starts with ```json
  # find last line that ends with ```
  # return the content between those two lines
  print(message)
  lines = message.split("\n")
  start = -1
  end = -1
  for i, line in enumerate(lines):
    if line.startswith("```"):
      if start == -1:
        start = i
      else:
        end = i
        break
  # print(lines)
  if start == -1 or end == -1:
    return None
  # print("\n".join(lines[start+1:end]))
  try:
    tests_created = json.loads("\n".join(lines[start+1:end]), strict=False)
    return tests_created
  except:
    return None

def create_code(imports, test, test_file):
  for imp in imports:
    test_file = f"{imp}\n" + test_file
  test_file += f"\n{test}"
  return test_file

def get_coverage_percentage(cr):
  if cr == None:
    return 0
  return float(cr.split("\n")[0].split()[-1][:-1])

testFilePath = sys.argv[1]
projectPath = sys.argv[2]
sourceCode = sys.argv[3]

generated_test_file_path = os.path.join(os.path.dirname(testFilePath), os.path.basename(testFilePath).split(".")[0] + "_tmp.py")


with open(generated_test_file_path, "w") as file:
  file.write(open_file(testFilePath))

testFilePath = generated_test_file_path

source_file_numbered = open_file_and_number(os.path.join(projectPath, sourceCode))

dependencies = files_gatherer.main_function(testFilePath, projectPath)

tests_files = []
ast.parse(open_file(testFilePath))
# find def test_ functions
# add them to tests_files
for node in ast.walk(ast.parse(open_file(testFilePath))):
  if isinstance(node, ast.FunctionDef):
    if node.name.startswith("test_"):
      tests_files.append(ast.unparse(node))

additional_includes = []
for dependency in dependencies:
  file_name = os.path.basename(dependency)
  code = open_file(dependency)
  d = {}
  d["file_name"] = file_name
  d["code"] = code
  additional_includes.append(d)
  print(d)

failed_tests = []

iteration = 0
while iteration < 100:
  iteration += 1
  coverage_report = coverage_gatherer.main(projectPath, testFilePath, sourceCode)
  print(coverage_report)
  if get_coverage_percentage(coverage_report) == 100:
    break
  print(f"ITERATION: {iteration}")
  prompt = (prompt_generation.prompt_generation(sourceCode, source_file_numbered, tests_files, os.path.basename(testFilePath) , failed_tests, additional_includes, coverage_report))
  created_tests = parse_json(llm_chat.get_response(prompt))
  if created_tests == None:
    continue
  previous_test_code = ""
  good_test_found = 0
  with open(testFilePath, "r") as f:
    previous_test_code = f.read()
  for test in created_tests:
    test_code = create_code(test["imports"], test["test_code"], previous_test_code)
    with open(testFilePath, "w") as f:
      f.write(test_code)
    cr = coverage_gatherer.main(projectPath, testFilePath, sourceCode)
    if cr == None:
      continue
    if get_coverage_percentage(cr) > get_coverage_percentage(coverage_report):
      good_test_found = 1
      break
    else:
      failed_tests.append(test_code)
  if not good_test_found:
    with open(testFilePath, "w") as f:
      f.write(previous_test_code)
