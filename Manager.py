import sys
import os
import subprocess
import yaml
import glob
import csv

def cloneFile(original_file):
    with open(original_file, 'rb') as original:
        new_file = "copy_" + original_file
        with open(new_file, 'wb') as new:
            new.write(original.read())
        return new_file
    return ""

def getFilesToCreate():
    files = []
    for scope in readYAML()["records"]["scope"]:
        files.append(scope["file"])
    return files

def getFileContentToWrite(file):
    for scope in readYAML()["records"]["scope"]:
        if file == scope["file"]:
            return scope["columns"]

def createFiles():
    files = getFilesToCreate()
    for file_path in files:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                csv_writer = csv.writer(file)
                print(getFileContentToWrite(file_path))
                csv_writer.writerow(getFileContentToWrite(file_path))

def cleanFiles(file_list):
    files = readYAML()['delete_files']['files']
    for extension in readYAML()['delete_files']['extensions']:
        files += glob.glob(extension)
    files = files + file_list

    for filename in os.listdir("./"):
        if filename.startswith("copy_"):
            files.append(os.path.join("./", filename))

    for file in files:
        try:
            os.remove(file)
        except FileNotFoundError:
            continue
        except PermissionError:
            print(f"Permission denied: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}")

def findAndReplaceInCommand(command, arguments, file, metric):
    for index, element in enumerate(command):
        for argument in arguments:
            element = element.replace(argument['find'], argument['replace'])
        element = element.replace("file", file)
        element = element.replace("metric", metric)
        command[index] = element
    return command

def readYAML():
    with open("configurations.yaml", 'r') as file:
        return yaml.safe_load(file)

def readCommands():
    data = readYAML() 

    if 'module_commands' not in data:
        raise KeyError("The key 'module_commands' is not found in the YAML file.")

    module_commands = data['module_commands']
    translated_dict = {}

    for module in module_commands:
        if 'name' not in module or 'command' not in module:
            raise KeyError("Each module must have 'name' and 'command' keys.")

        name = module['name']
        command = module['command']

        if not isinstance(command, list):
            raise TypeError(f"The 'command' for module {name} must be a list.")

        translated_dict[name] = command

    return translated_dict

def readArguments():
    data = readYAML() 

    if 'functionalities_arguments' not in data:
        raise KeyError("The key 'functionalities_arguments' is not found in the YAML file.")

    functionalities_arguments = data['functionalities_arguments']
    translated_dict = {}

    for functionality in functionalities_arguments:
        if 'name' not in functionality or 'arguments' not in functionality:
            raise KeyError("Each functionality must have 'name' and 'arguments' keys.")

        name = functionality['name']
        arguments = functionality['arguments']

        if not isinstance(arguments, list):
            raise TypeError(f"The 'arguments' for functionality {name} must be a list.")

        translated_dict[name] = arguments

    return translated_dict

def readSequences():
    data = readYAML() 

    if 'functionalities_sequences' not in data:
        raise KeyError("The key 'functionalities_sequences' is not found in the YAML file.")

    functionalities_sequences = data['functionalities_sequences']
    translated_dict = {}

    for functionality in functionalities_sequences:
        if 'name' not in functionality or 'steps' not in functionality:
            raise KeyError("Each functionality must have 'name' and 'steps' keys.")

        name = functionality['name']
        steps = functionality['steps']

        if not isinstance(steps, list):
            raise TypeError(f"The 'steps' for functionality {name} must be a list.")

        translated_dict[name] = steps

    return translated_dict

def getCommand(functionality, module, file, metric):
    arguments = readArguments()
    commands = readCommands()
    return findAndReplaceInCommand(commands[module], arguments[functionality], file, metric)

def runFile(command):
    result = subprocess.run(command, capture_output=True, text=True)
    # Check if the command was successful
    if result.returncode != 0:
        print(f"Command failed! ({command}) ")
        print("Error message:")
        print(result.stderr)
        return -1
    else:
        print(result.stdout)

def runSequence(functionality, file, metric):
    sequence = readSequences()[functionality]
    for element in sequence:
        command = getCommand(functionality, element, file, metric)
        runFile(command)

def main():
    if len(sys.argv) < 3:
        print("Usage: python Manager.py -comparison [-full file1 file2 | -segment file1 file2] metric | -analysis -line | -full file1 metric")
        return

    action = sys.argv[1]

    if action != "-comparison" and action != "-analysis":
        print("Invalid action. Please specify -comparison or -analysis")

    createFiles()

    if sys.argv[2] == "-full" and action == "-comparison" and (len(sys.argv) == 7 or len(sys.argv) == 6):
        #Run compare files sequence
        file1 = sys.argv[3]
        file2 = sys.argv[4]

        metric = sys.argv[5]

        runSequence("fullComparison", file1, metric)
        runSequence("fullComparison", file2, metric)

        cleanFiles([file1.rsplit('.', 1)[0], file2.rsplit('.', 1)[0]])

    elif sys.argv[2] == "-segment" and action == "-comparison" and (len(sys.argv) == 7 or len(sys.argv) == 6):
        #Run compare segment sequence
        file1 = sys.argv[3]
        copy_file1 = cloneFile(file1)

        file2 = sys.argv[4]
        copy_file2 = cloneFile(file2)

        metric = sys.argv[5]

        runSequence("segmentComparison", copy_file1, metric)
        runSequence("segmentComparison", copy_file2, metric)

        cleanFiles([copy_file1.rsplit('.', 1)[0], copy_file2.rsplit('.', 1)[0]])

    elif sys.argv[2] == "-line" and action == "-analysis" and (len(sys.argv) == 5 or len(sys.argv) == 6):
        #Run analyze files sequence
        file1 = sys.argv[3]
        copy_file1 = cloneFile(file1)

        metric = sys.argv[4]

        runSequence("lineAnalysis", copy_file1, metric)

        cleanFiles([copy_file1.rsplit('.', 1)[0]])

    elif sys.argv[2] == "-full" and action == "-analysis" and (len(sys.argv) == 5 or len(sys.argv) == 6):
        #Run analyze file sequence
        file1 = sys.argv[3]
        metric = sys.argv[4]
        
        runSequence("fullAnalysis", file1, metric)

        cleanFiles([file1.rsplit('.', 1)[0]])

    else:
        print("Invalid arguments. Please check usage.")


    

if __name__ == "__main__":
    main()