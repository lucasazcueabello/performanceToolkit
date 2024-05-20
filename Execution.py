import subprocess
import yaml
import sys

def readYAML():
    with open("configurations.yaml", 'r') as file:
        return yaml.safe_load(file)

def getToolExecution(metric):
    tools = readYAML()["measurement_tools"]
    for tool in tools:
        if tool["metric"] == metric:
            return tool["path"]
    return tools[0]["path"]

def getUpdatedCommand(replacements, list):
    updated_command = []
    for element in list:
        replaced = False
        for find, replace in replacements.items():
            if element == find:
                updated_command.append(replace)
                replaced = True
                break
        if not replaced:
            updated_command.append(element)
    return updated_command

def getExecuteCommand(file):  
    extension = file.rsplit('.', 1)[1]
    languages = readYAML()["languages"]
    for language in languages:
        if language["extension"] == extension:
            return getUpdatedCommand({"file": file, "./executable_file": "./" + file.rsplit('.', 1)[0]}, language["execution"])

def makeMeasurement(metric, string):
    tools = readYAML()["measurement_tools"]
    for tool in tools:
        if tool["metric"] == metric:
            result = subprocess.run(getUpdatedCommand({"-string": "-" + string, "toolPath": tool["path"]}, tool["command"]), capture_output=True, text=True)
            # Check if the command was successful
            if result.returncode != 0:
                print("Command failed!")
                print("Error message:")
                print(result.stderr)

def executeFile(file, metric):
    result = subprocess.run(getExecuteCommand(file), capture_output=True, text=True)
    # Check if the command was successful
    if result.returncode != 0:
        print("Command failed!")
        print("Error message:")
        print(result.stderr)
        return -1

def measureAndExecute(file, metric):
    makeMeasurement(metric, "before")
    executeFile(file, metric)
    makeMeasurement(metric, "after")

def main():
    if len(sys.argv) != 4:
        print("Invalid Arguments for the Execution module")
        return

    if sys.argv[1] != "full" and sys.argv[1] != "line" and sys.argv[1] != "segment":
        print("Invalid action. Please specify -full, -segment or -line for the Execution Module")
        return

    if sys.argv[1] == "full":
        #Measure-Run-Measure
        measureAndExecute(sys.argv[3], sys.argv[2])
    else:
        #Run
        executeFile(sys.argv[3], sys.argv[2])


    
if __name__ == "__main__":
    main()