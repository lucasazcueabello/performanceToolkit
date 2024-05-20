import sys
import yaml
import subprocess
import os
import glob

def readYAML():
    with open("configurations.yaml", 'r') as file:
        return yaml.safe_load(file)

def getUpdatedCommand(file, executable_file, command):
    updated_command = []
    for element in command:
        if element == "file":
            updated_command.append(file)
        elif element == "executable_file":
            updated_command.append(executable_file)
        elif '*' in element and element.startswith('*.') and len(element) > 2:
            extension = element[1:]
            matching_files = glob.glob(f"*{extension}")
            updated_command.extend(matching_files)
        else:
            updated_command.append(element)
    return updated_command

def runCompilation(file, executable_file, command):
    command = getUpdatedCommand(file, executable_file, command)
    result = subprocess.run(command, capture_output=True, text=True)
    # Check if the command was successful
    if result.returncode != 0:
        print("Command failed!")
        print("Error message:")
        print(result.stderr)

def compileFile(file):
    languages = readYAML()['languages']

    for language in languages:
        if language["extension"] == file.rsplit('.', 1)[1] and 'compilation' in language:
            executable_file = file.rsplit('.', 1)[0]
            runCompilation(file, executable_file, language["compilation"])

def main():
    if len(sys.argv) != 2:
        print("Invalid Arguments for the Compilation module")
        return

    #Call compilation method
    compileFile(sys.argv[1])
    
if __name__ == "__main__":
    main()