import csv
import yaml
import matplotlib.pyplot as plt
import sys

def readYAML():
    with open("configurations.yaml", 'r') as file:
        return yaml.safe_load(file)

def getMetricInfo(key, metric):
    data = readYAML()["measurement_tools"]
    for element in data:
        if element["metric"] == metric:
            return element[key]
    return data[0][key]

def getScope(scope):
    for scopes in readYAML()["records"]["scope"]:
        if scopes["name"] == scope:
            return scopes
    return readYAML()["records"]["scope"][0]

def getScopeFile(scope):
    return getScope(scope)["file"]

def getRecordHeader(scope):
    return getScope(scope)["columns"]

def isFileIncluded(file, data):
    for element in data:
        if element[0] == file:
            return True
    return False

def getElementsFromCSV(file, metric, scope):
    data = []
    index = int(getMetricInfo("records_index", metric))
    file_path = getScopeFile(scope)

    with open(file_path, 'r', newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        lines = sum(1 for _ in csvfile)
        csvfile.seek(0)
        if lines == 1:
            return []
        csv_reader = list(csv.reader(csvfile))
        for row in reversed(csv_reader):
            if row[0].rsplit('.', 1)[0] == file.rsplit('.', 1)[0] and not isFileIncluded(row[0], data) and float(row[index]) > 0.0:
                data.append((row[0], float(row[index])))
            if len(data) >= len(readYAML()["languages"]):
                return data
    return data

def plotBarGraphic(columns, measurements, metric, concept, title, save_path=None):
    lines = [item for item in columns]
    measurement = [item for item in measurements]
    
    plt.figure(figsize=(10, 6))  # Adjust the figure size as needed
    plt.bar(lines, measurement)
    plt.xlabel(concept)
    plt.ylabel(metric + "(" + getMetricInfo("unit", metric) + ")")
    plt.title(metric + ' '  + title)
    
    if save_path:
        plt.savefig(save_path)  # Save graph as image file
        plt.close()  # Close the figure to release resources
    else:
        plt.show()  # Display the graph interactively

def representComparison(file, metric, scope):
    data = getElementsFromCSV(file, metric, scope)
    measurements = [item[1] for item in data]
    files = [item[0] for item in data]
    plotBarGraphic(files, measurements, metric, "Files", "comparison between programming languages", metric + "_languages_comparison.png")


def main():
    if len(sys.argv) != 4:
        print("Invalid Arguments for the LanguageComparison module")
        return

    if sys.argv[1] == "full":
        representComparison(sys.argv[3], sys.argv[2], sys.argv[1])


    
if __name__ == "__main__":
    main()