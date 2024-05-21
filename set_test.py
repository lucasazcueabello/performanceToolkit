import sys

# Define the test functions

def test_set_iteration(set_data):
    for item in set_data:
        pass

def test_set_addition(set_data):
    for i in range(len(set_data), 2*len(set_data)):
        set_data.add(i)

def test_set_deletion(set_data):
    for i in range(len(set_data)):
        set_data.remove(i)


# Measure the execution time of each operation
# Sample sizes for testing
n = sys.argv[1]
elements = list(range(int(n)))

# Define the data structure
set_data = set(elements)

#Begin
test_set_iteration(set_data)
#End

test_set_addition(set_data)

test_set_deletion(set_data)
