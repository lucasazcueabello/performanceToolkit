import yaml
import sys

def readYAML():
    with open("configurations.yaml", 'r') as file:
        return yaml.safe_load(file)

def addLibraries(file_path, libraries):
    # Read the contents of the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for library in libraries:
        # Shift all lines below by one line
        for i in range(len(lines) - 1, 0, -1):
            lines[i] = lines[i - 1]

        lines[0] = "import " + library + "\n"

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.writelines(lines)

def importLibraries(file):
    languages = readYAML()["languages"]
    for language in languages:
        if language["extension"] == file.rsplit('.', 1)[1] and 'libraries' in language:
            addLibraries(file, language["libraries"])

def main():
    if len(sys.argv) != 2:
        print("Invalid Arguments for the Libraries module")
        return
    
    importLibraries(sys.argv[1])

    
if __name__ == "__main__":
    main()