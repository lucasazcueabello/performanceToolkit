import sys
import yaml

def readYAML():
    with open("configurations.yaml", 'r') as file:
        return yaml.safe_load(file)

def getToolExecution(metric):
    tools = readYAML()["measurement_tools"]
    for tool in tools:
        if tool["metric"] == metric:
            return tool["path"]
    return tools[0].path

def getFileComments(file):
    languages = readYAML()['languages']
    for lang in languages:
        if lang["extension"] == file.rsplit('.', 1)[1]:
            return lang["comments"][0]["find"], lang["comments"][1]["find"]
    return languages[0]["comments"][0]["find"], languages[0]["comments"][1]["find"]

def getFileCommand(file, metric, name):
    languages = readYAML()['languages']
    for lang in languages:
        if lang["extension"] == file.rsplit('.', 1)[1]:
            for comment in lang["comments"]:
                if comment["name"] == name:
                    return comment["replace"].replace("toolPath", getToolExecution(metric))
    return languages[0]["comments"][0]["replace"].replace("toolPath", getToolExecution(metric))

def findAndReplaceInFile(file_path, old_string, new_string):
    # Read the content of the file
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Perform the replacement operation
    modified_content = file_content.replace(old_string, new_string)

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.write(modified_content)

def addCommentsBetweenStrings(file_path, start_string, end_string, comment='# Execute tool for line'):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    between_strings = False
    line_number = 0

    for idx, line in enumerate(lines):
        modified_lines.append(line)
        line_number = line_number + 1
        if start_string in line:
            between_strings = True
        elif end_string in line:
            between_strings = False
        if between_strings:
            next_indent = 0  # Default indentation for the next line
            if idx < len(lines) - 1:  # Check if it's not the last line
                next_line = lines[idx + 1]  # Get the next line
                if next_line == '\n' or '}' in next_line:  # Check if the next line is not empty
                    next_indent = len(line) - len(line.lstrip())  # Calculate the indentation level of the current line
                else:
                    next_indent = len(next_line) - len(next_line.lstrip())  # Calculate the indentation level of the next line
            indentation = ''
            if next_indent > 0:
                for _ in range(next_indent):  # Loop to add spaces dynamically
                    indentation = indentation + ' '  # Add a space for each indentation level                 
            modified_lines.append(indentation + comment.replace('line_count', str(line_number)) + '\n')

    with open(file_path, 'w') as file:
        file.writelines(modified_lines)

def segmentComments(file, metric):
    begin, end = getFileComments(file)
    findAndReplaceInFile(file, begin, getFileCommand(file, metric, "begin"))
    findAndReplaceInFile(file, end, getFileCommand(file, metric, "end"))

def lineComments(file, metric):
    begin_string, end_string = getFileComments(file)
    addCommentsBetweenStrings(file, begin_string, end_string, getFileCommand(file, metric, "line"))

def main():
    if len(sys.argv) != 4:
        print("Invalid Arguments for the Comments module")
        return
    
    if sys.argv[1] != "segment" and sys.argv[1] != "line":
        print("Invalid action. Please specify -segment or -line for the Comments Module")
        return

    if sys.argv[1] == "segment":
        segmentComments(sys.argv[3], sys.argv[2])
    else:
        lineComments(sys.argv[3], sys.argv[2])

    

if __name__ == "__main__":
    main()