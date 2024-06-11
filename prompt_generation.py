def prompt_generation(source_file_name, source_file_numbered, tests_files, test_file_name, failed_tests, needed_modules, code_coverage):
  intro_prompt = """
You are a Python code assistant.
You will be given a Python source file and, optionally, an accompanying Python test file.
Your task is to create additional unit tests to enhance the existing test suite, aiming for complete code coverage.

Be sure to follow these steps to complete the task successfully:
1. Thoroughly review the provided source code in detail. Take note of its its behaviour, funtionality logic, inputs and outputs.
2. Generate a comprehensive list of test cases needed to fully verify the code's accuracy and achieve maximum code coverage, including handling exceptions and errors.
3. Add each test individually, then review the entire test suite to ensure all scenarios are covered.
4. Avoid duplicating tests that have already been written, especially those that have failed in previous iterations.
5. Ensure that each test is independent, isolated, and does not rely on the state of other tests.
6. If the original test file contains a test suite, integrate the new tests into it, maintaining consistency in style, naming conventions, and structure.
7. Make sure each test only calls a function once and that only one assertion is made per test function.
"""
  source_file_prompt = f"""`Source File`
Here is the source file which you will be writing tests for, with line numbers added manually for easier comprehension: {source_file_name}.
```
{source_file_numbered}
```
"""
  tests_files_prompt = """"""
  if len(tests_files) > 0:
    tests_files_prompt = f"""
`Test File`
Here is a python test file with numbers added manually added for easier comprehension: {test_file_name}. 
```
"""
    for test in tests_files:
      tests_files_prompt += f"{test}\n---------\n"
  else:
    tests_files_prompt = f"""
`Test File`
There are no test files provided. You will be writing tests for the source file based on just the source file which contains the code to be tested.
"""
  failed_tests_prompt = ""
  if len(failed_tests) > 0:
    failed_tests_prompt = f"""
`Previous Iterations Failed Tests`
Below is a list of failed tests or tests that didn't improve coverage that you generated in previous iterations. Do not generate the same tests again, and take the failed tests into account when generating new tests.
```
"""
    for failed_test in failed_tests:
      failed_tests_prompt += f"{failed_test}\n---------\n"
    failed_tests_prompt += "--------"
  else:
    failed_tests_prompt = "```"
  needed_modules_prompt = ""
  if needed_modules != None:
    needed_modules_prompt = """

`Libraries or additional files used`
The following is a set of included files used as context for the source code above. This is usually included libraries needed as context to write better tests:
```

"""
    for module in needed_modules:
      needed_modules_prompt += f"---- {module['file_name']} ----\n{module['code']}\n"
    needed_modules_prompt += '```'
  code_coverage_prompt = f"""
The goal is to achieve maximum code coverage. The code coverage is currently at {code_coverage.split()[2] if code_coverage else 0}%, find the coverage report below:
```
{code_coverage}
```
"""
  response_format_prompt = """
`Response`
The response should be valid json file with the following format:
```json
[{
  "test_name": "test_TESTNAME",
  "test_code": "PYTHON CODE",
  "imports": [IMPORTS_NEDED],
  "preprocessing_code": "PYTHON CODE",
},
...
]
```
Where:
TESTNAME: The name of the test. It should be unique.
IMPORTS_NEEDED: A list of imports that are needed for the test to run.
PYTHON CODE: The python code for the test. This should be a valid python code that tests the source file.
Use ' for strings. Python code should be indented. Do not use triple " for strings. Use \n and spaces for new lines and indentation.
------
Example output:
[{
  "test_name": "test_addition",
  "test_code": "def test_addition():\n  assert addition(1, 2) == 3",
  "imports": ["from my_module import addition"],
  "preprocessing_code": ""
},
...,
]

Response should be a valid json file, and nothing else, I repeat again, only json file.
"""
  return intro_prompt + source_file_prompt + tests_files_prompt + failed_tests_prompt + needed_modules_prompt + code_coverage_prompt + response_format_prompt