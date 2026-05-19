import math

def number_calculations():
    num1,num2 = float(input("Enter a number: ").split())

    square = num1** 2
    cube = num2 ** 3
    square_root = math.sqrt(num1) if num1 >= 0 else "Not defined for negative numbers"
    double = num2 * 2

    print("\nResults:")
    print("Square:", square)
    print("Cube:", cube)
    print("Square Root:", square_root)
    print("Double:", double)

# Call the function
number_calculations()