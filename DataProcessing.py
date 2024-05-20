import csv
import yaml
import matplotlib.pyplot as plt
import sys

def readYAML():
    with open("configurations.yaml", 'r') as file:
        return yaml.safe_load(file)

def removeCopyPrefix(filename):
    prefix = "copy_"
    if filename.startswith(prefix):
        return filename[len(prefix):]
    return filename

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

def computeLineMeasurements(data):
    energy_differences = []
    for i in range(0, len(data) - 1):
        energy_diff = data[i+1][0] - data[i][0]
        energy_differences.append((energy_diff, data[i+1][1]))
    return getAverageFromRepeatingValues(energy_differences)

def getAverageFromRepeatingValues(data):
    sums_counts = {}
    
    for value, key in data:
        if key in sums_counts:
            sums_counts[key]['sum'] += value
            sums_counts[key]['count'] += 1
        else:
            sums_counts[key] = {'sum': value, 'count': 1}
    
    averages = [(key, sums_counts[key]['sum'] / sums_counts[key]['count']) for key in sums_counts]    
    return averages

def parseFile(file_path, symbol):
    data_structure = []

    with open(file_path, 'r') as file:
        lines = sum(1 for _ in file)
        file.seek(0)  # Reset file pointer to the beginning
        if lines > 2:
            for line in file:
                parts = line.split(symbol)
                if len(parts) == 2:
                    result = float(parts[0])
                    line_number = int(parts[1])
                    data_structure.append((result, line_number))
            return computeLineMeasurements(data_structure)

        elif lines == 2:
            for line in file:
                parts = line.split(symbol)
                if len(parts) == 2:
                    result = float(parts[0])
                    data_structure.append(result)
            if len(data_structure) == 2:  # Ensure there are two elements
                return data_structure[1] - data_structure[0]
            else:
                raise ValueError("Not enough valid data in the file")

        else:
            sys.exit(0)

def operateData(metric):
    tools = readYAML()["measurement_tools"]
    for tool in tools:
        if tool["metric"] == metric:
            return parseFile(tool["file"], tool["symbol"])

def checkIfMeasurementSaved(file, new_row):
    last_csv_value = None
    with open(file, mode='r', newline='') as csvfile:
        csvfile.seek(0)
        reader = csv.reader(csvfile)
        for row in reader:
            if row:
                last_row = row
    if last_row == new_row:
        return True
    else:
        return False

def saveToCSV(file, measurement, metric, scope):
    index = int(getMetricInfo("records_index", metric))
    csv_file = getScopeFile(scope)
    with open(csv_file, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        measurement_tools = readYAML()["measurement_tools"]
        row = [file]
        for x in range(0, len(measurement_tools)):
            row.append(str(0.0))
        row[index] = str(measurement)
        if not checkIfMeasurementSaved(csv_file, row): 
            csv_writer.writerow(row)

def getComparisonElement(file, metric, scope):
    index = int(getMetricInfo("records_index", metric))
    file_path = getScopeFile(scope)
    with open(file_path, 'r', newline='') as csvfile:
        lines = sum(1 for _ in csvfile)
        csvfile.seek(0)
        if lines <= 1:
            return "NA", 0.0
        csv_reader = list(csv.reader(csvfile))
        for row in reversed(csv_reader):
            if row == getRecordHeader(scope):
                return "NA", 0.0
            if float(row[index]) > 0.0 and file != row[0]:
                return row[0], float(row[index])
    return "NA", 0.0

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
        next(csv_reader)
        for row in csv_reader:
            if row[0] == file and float(row[index]) > 0.0:
                data.append((float(row[index])))
    return data

def getTotalMeasurement(data):
    total = 0
    for element in data:
        total += element[1]
    return total

def plotBarGraphic(columns, measurements, metric, concept, title, save_path=None):
    lines = [item for item in columns]
    measurement = [item for item in measurements]
    
    plt.bar(lines, measurement)
    plt.xlabel(concept)
    plt.ylabel(metric + "(" + getMetricInfo("unit", metric) + ")")
    plt.title(metric + ' '  + title)
    
    if save_path:
        plt.savefig(save_path)  # Save graph as image file
        plt.close()  # Close the figure to release resources
    else:
        plt.show()  # Display the graph interactively

def plotLineGraph(file, records, metric, save_path=None):
    values = readYAML()["records"]["max_values"]
    if len(records) > values and values > 0:
        measurements = [entry for entry in records[len(records) - values:]]
    else:
        measurements = [entry for entry in records]

    x_values = range(1, len(measurements) + 1)
    plt.plot(x_values, measurements)
    plt.xlabel('Instances of ' + file)
    plt.ylabel(metric + "(" + getMetricInfo("unit", metric) + ")")
    plt.title(file + ' progression')

    if save_path:
        plt.savefig(save_path)  # Save graph as image file
        plt.close()  # Close the figure to release resources
    else:
        plt.show()  # Display the graph interactively

def printResults(file, result1, metric, unit):
    print()
    print(file + " measurements:")
    print("     " + metric +": " + str(result1) + " " + unit)
    print()

def printComparison(file1, file2, result1, result2, metric):
    unit = getMetricInfo("unit", metric)
    printResults(file1, result1, metric, unit)
    printResults(file2, result2, metric, unit)

    print()
    print("Difference:")
    print("     " + metric +": " + str(abs(result1 - result2)) + " " + unit)
    print()

def comparison(file, metric, scope):
    result = operateData(metric)
    comparison_file_name, comparison_result = getComparisonElement(file, metric, scope)
    saveToCSV(file, result, metric, scope)
    plotBarGraphic([comparison_file_name, file], [comparison_result, result], metric, "Files", "comparison between full files", metric + "_comparison.png")
    printComparison(comparison_file_name, file, comparison_result, result, metric)

def multiline(file, metric, scope):
    results = operateData(metric)
    total_measurement = getTotalMeasurement(results)
    saveToCSV(file, total_measurement, metric, scope)
    measurements = [item[1] for item in results]
    lines = [item[0] for item in results]
    plotBarGraphic(lines, measurements, metric, "Line Number", "line analysys for " + file + " segment", metric + "_line_analysis.png")
    printResults(file, total_measurement, metric, getMetricInfo("unit", metric))

def progression(file, metric, scope):
    result = operateData(metric)
    records = getElementsFromCSV(file, metric, scope) + [result]
    saveToCSV(file, result, metric, scope)
    plotLineGraph(file, records, metric, metric + "_full_analysis.png")
    printResults(file, result, metric, getMetricInfo("unit", metric))


def main():
    if len(sys.argv) != 5:
        print("Invalid Arguments for the DataProcessing module")
        return
    
    if sys.argv[1] != "lineChart" and sys.argv[1] != "barChart":
        print("Invalid action. Please specify -segment or -line for the Comments Module")
        return

    if sys.argv[1] == "barChart" and sys.argv[2] == "line":
        multiline(removeCopyPrefix(sys.argv[4]), sys.argv[3], sys.argv[2])
    elif sys.argv[1] == "barChart" and sys.argv[2] != "line":
        comparison(removeCopyPrefix(sys.argv[4]), sys.argv[3], sys.argv[2])
    elif sys.argv[1] == "lineChart" and sys.argv[2] == "full":
        progression(removeCopyPrefix(sys.argv[4]), sys.argv[3], sys.argv[2])


    
if __name__ == "__main__":
    main()