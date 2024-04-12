# math.py
import math
import spacy
import sympy as sp

class MathHelper:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        self.operations = {
            'add': (["add", "sum", "plus","addition", "i want to add","lets add"],self.add),
            'subtract': (["subtract", "minus", "difference","subtraction","i want to subtract", "lets subtract"],self.subtract),
            'multiply': (["multiply", "product", "times","multiplication", "i want to multiply", "lets multiply"],self.multiply),
            'divide': (["divide", "division", "quotient","division","i want to divide","lets divide"],self.divide),
            'power': (['power', 'exponent', 'raised to','squared'],self.power),
            'square root': (['square root', 'sqrt','sqr root'],self.square_root),
            'derivative': (["derivative", "derivation", "differentiate", "find the derivative",], self.derivative)
            # Add more math operations as needed
        }

    def derivative(self, expression):
        expression = expression.replace('x','*x')
        try:
            expr = sp.sympify(expression)
        except sp.SympifyError:
            return "Invalid mathematical expression."
        variables = list(expr.free_symbols)
        if not variables:
            return "The expression does not contain any variables"
        print("Available variables:", ', '.join(str(var) for var in variables))
        var_names = input("Enter the variable(s) to differentiate with respect to (comma-seperated): ").split(',')
        var_names = [name.strip() for name in var_names]
        result = expr
        for var_name in var_names:
            var = sp.Symbol(var_name)
            if var not in variables:
                return f"Variable '{var_name}' not found in the expression."
            result = sp.diff(result, var)
        return str(result)

    def add(self, num1, num2):
        return num1 + num2

    def subtract(self, num1, num2):
        return num1 - num2

    def multiply(self, num1, num2):
        return num1 * num2

    def divide(self, num1, num2):
        if num2 != 0:
            return num1 / num2
        else:
            raise ValueError("Division by zero is not allowed.")

    def power(self, base, exponent):
        return math.pow(base, exponent)

    def square_root(self, num):
        if num >= 0:
            return math.sqrt(num)
        else:
            raise ValueError("Square root of a negative number is not allowed.")

    # Add more math functions as needed

    def find_operation(self, user_input):
        input_doc = self.nlp(user_input.lower())
        max_similarity = -1
        matched_operation = None

        for operation, (keywords, _) in self.operations.items():
            for keyword in keywords:
                keyword_doc = self.nlp(keyword)
                similarity = input_doc.similarity(keyword_doc)
                if similarity > max_similarity:
                    max_similarity = similarity
                    matched_operation = operation

        return matched_operation

    def perform_operation(self, user_input, *args):
        operation = self.find_operation(user_input)
        if operation:
            func = self.operations[operation][1]
            return func(*args)
        else:
            raise ValueError(f"Unsupported math operation: {user_input}")