# math.py
import math
import spacy
import sympy as sp
import re
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
            'derivative': (["derivative", "derivation", "differentiate", "find the derivative",], self.derivative),
            'summation': (['summation','sigma',], self.summation),
            'limit': (['limit','lim', 'find the limit'], self.limit),
            'help': (['i need help', 'what operations are available', 'assistance', "help me", "what can i do", "options", "what are the options","what can you do"," "],self.help),
            'equation': (['solve equation','solve for', 'find the value'], self.equation),
            'system of equations': (['solve system of equations', 'linear equations', 'simultaneous equations', "sys of eq"], self.solve_system_of_equations),
        }
    def help(self):
        commands = {
            'add': 'adds two numbers',
            'subtract': 'subtract two numbers',
            'multiply': 'multiply two numbers',
            'divide': ' divide two numbers',
            'power': 'take the power of a number',
            'square root': 'take the square root of a number',
            'derivative': 'take the derivative of an expression',
            'summation': 'find the summation of an expression',
            'limit': 'take the limit of an expression',
            'solve': 'solves general equations',
        }
        return (commands)

    def solve_system_of_equations(self, equations):
        try:
            #print("Original equations:", equations)  # Debug
        # Insert multiplication signs where necessary
            equations = [re.sub(r'(\d)([a-zA-Z])', r'\1*\2', eq.replace('=', '-')) for eq in equations]
            #print("Transformed equations with explicit multiplication:", equations)  # Debug
            equations = [sp.sympify(eq) for eq in equations]
            #print("Sympified equations:", equations)  # Additional debug to verify sympy expressions
            variables = set()
            for eq in equations:
                variables.update(eq.free_symbols)
            #print("Variables detected:", variables)  # Debug
            if not variables:
                return "No variables found."
            solution = sp.linsolve(equations, *variables)
            if not solution:
                return "No solution or infinite number of solutions."
            return str(solution)
        except Exception as e:
            return f"Invalid system of equations due to input error: {str(e)}"


    def equation(self, equation, variable):
        equation = re.sub(r'(\d)(\()', r'\1*\2', equation)
        equation = re.sub(r'(\))(\d)', r'\1*\2', equation)
        equation = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', equation)
        equation = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', equation)
        equation = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', equation)
        equation = re.sub(r'=',r'-', equation)
        try:
            expr = sp.sympify(equation)
            var = sp.Symbol(variable)
            solution = sp.solveset(expr, var, domain=sp.Reals)

            if isinstance(solution, sp.sets.EmptySet):
                return "No solution found."
            elif isinstance(solution, sp.sets.FiniteSet):
                return f"The solution is: {', '.join(str(sol) for sol in solution)}"
            elif isinstance(solution, sp.sets.Interval):
                return f"The solution is in the interval: {solution}"
            else:
                return "Unable to determine the type of solution... Try another method?"
        except sp.SympifyError:
            return "Invalid equation."

    def summation(self, expression, lower_limit, upper_limit, variable):
        expression = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expression)
        expression = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expression)
        expression = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expression)
        try:
            expr = sp.sympify(expression)
            var = sp.Symbol(variable)
            lower = sp.sympify(lower_limit)
            upper = sp.sympify(upper_limit)
            result = sp.summation(expr, (var, lower, upper))
            return str(result)
        except sp.SympifyError:
            return "Invalid mathematical expression."
    
    def limit(self, expression, variable, approaching_value):
        expression = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expression)
        expression = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expression)
        expression = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expression)
        try:
            expr = sp.sympify(expression)
            var = sp.Symbol(variable)
            approaching = sp.sympify(approaching_value)
            result = sp.limit(expr, var, approaching)
            return str(result)
        except sp.SympifyError:
            return "Invalid mathematical expression."

    def derivative(self, expression):
        # Replace implicit multiplication with explicit multiplication
        expression = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expression)
        expression = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expression)
        expression = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expression)

        try:
            expr = sp.sympify(expression)
        except sp.SympifyError:
            return "Invalid mathematical expression."

        variables = list(expr.free_symbols)

        if not variables:
            return "The expression does not contain any variables."

        print("Available variables:", ', '.join(str(var) for var in variables))
        var_names = input("Enter the variable(s) to differentiate with respect to (comma-separated): ").split(',')
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