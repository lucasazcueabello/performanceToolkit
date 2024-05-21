import sys

# Define the test functions
def test_list_iteration(list_data):
    for item in list_data:
        pass

def test_list_addition(list_data):
    for i in range(len(list_data), 2*len(list_data)):
        list_data.append(i)

def test_list_deletion(list_data):
    for i in range(len(list_data)):
        list_data.pop()

# Sample sizes for testing
n = sys.argv[1]
elements = list(range(int(n)))

# Define the data structures
list_data = elements.copy()

#Begin
test_list_iteration(list_data)
#End

test_list_addition(list_data)

test_list_deletion(list_data)
