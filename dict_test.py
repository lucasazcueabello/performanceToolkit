import sys

# Define the test functions

def test_dict_iteration(dict_data):
    for key in dict_data:
        pass

def test_dict_addition(dict_data):
    for i in range(len(dict_data), 2*len(dict_data)):
        dict_data[i] = None

def test_dict_deletion(dict_data):
    for i in range(len(dict_data)):
        dict_data.pop(i)

# Sample sizes for testing
n = sys.argv[1]
elements = list(range(int(n)))

# Define the data structure
dict_data = {i: None for i in elements}

#Begin
test_dict_iteration(dict_data)
#End

test_dict_addition(dict_data)

test_dict_deletion(dict_data)
