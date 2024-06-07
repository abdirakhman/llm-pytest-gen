import os
import subprocess
import json
import sys

def gather_coverage(working_dir, source_file_dir, concern_file_name):
  # Change working directory to working_dir
  # Run coverage command
  result = subprocess.run(["coverage", "run", "-m", "pytest", source_file_dir], cwd=working_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if result.returncode != 0:
    return None, None
  result = subprocess.run(["coverage", "json", "-o", "coverage.json"], cwd=working_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if result.returncode != 0:
    return None, None
  # Read coverage.json
  with open(os.path.join(working_dir, "coverage.json"), "r") as f:
    coverage_data = json.load(f)
  percent_covered = coverage_data["files"][concern_file_name]["summary"]["percent_covered"]
  missing_lines = coverage_data["files"][concern_file_name]["missing_lines"]
  os.remove(os.path.join(working_dir, "coverage.json"))
  return percent_covered, missing_lines

if __name__ == "__main__":
  working_dir = sys.argv[1]
  source_file_dir = sys.argv[2]
  concern_file_name = sys.argv[3]
  percent_covered, missing_lines = gather_coverage(working_dir, source_file_dir, concern_file_name)
  print(f"Coverage percentage: {percent_covered:.2f}%")
  print("Uncovered lines: ", end="")
  for line in missing_lines:
    print(line, end=" ")
  exit(0)


def main(working_dir, source_file_dir, concern_file_name):
  percent_covered, missing_lines = gather_coverage(working_dir, source_file_dir, concern_file_name)
  if percent_covered == None:
    return None
  coverage_percentage = f"Coverage percentage: {percent_covered:.2f}%"
  uncovered_lines = "Uncovered lines: "
  for line in missing_lines:
    uncovered_lines += str(line) + " "
  return coverage_percentage + "\n" + uncovered_lines