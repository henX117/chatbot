# math.py
import math
import spacy
import sympy as sp
import re
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

class MathHelper:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        self.operations = {
            'add': (["add", "sum", "plus","addition", "i want to add","lets add"],self.add),
            'subtract': (["subtract", "minus", "difference","subtraction","i want to subtract", "lets subtract","sub"],self.subtract),
            'multiply': (["multiply", "product", "times","multiplication", "i want to multiply", "lets multiply","mult"],self.multiply),
            'divide': (["divide", "division", "quotient","division","i want to divide","lets divide", 'div',],self.divide),
            'power': (['power', 'exponent', 'raised to','squared'],self.power),
            'square root': (['square root', 'sqrt','sqr root'],self.square_root),
            'derivative': (["derivative", "derivation", "differentiate", "find the derivative",], self.derivative),
            'summation': (['summation','sigma',], self.summation),
            'limit': (['limit','lim', 'find the limit'], self.limit),
            'help': (['i need help', 'what operations are available', 'assistance', "help me", "what can i do", "options", "what are the options","what can you do"," ", "operations"],self.help),
            'equation': (['solve equation','solve for', 'find the value'], self.equation),
            'system of equations': (['solve system of equations', 'linear equations', 'simultaneous equations', "sys of eq","system of equations"], self.solve_system_of_equations),
            'statistics': (['statistics', 'stats', 'statistical analysis', 'data analysis',],self.statistics),
            'finite series sum': (['finite series sum','series summation','sum of series','sum of a series',"series sum"], self.finite_series_sum),
            'graph': (['graph', 'plot', 'plot graph', 'draw graph', 'visualize'], self.graph),
            'quit':(['quit', 'exit', 'goodbye', 'bye', 'stop', 'end', 'no thanks', 'go back', 'return'], None)
        }
    
    def quit(self):
        return "Goodbye!"

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
            'system of equations': "solves for a variable of two or more equations",
            'statistics': 'performs basic stats like mean,median,mode,stdev,variance',
            'series summation': 'finds summation of a geometric or arithmetic series',
        }
        return (commands)
    
    def graph(self, expression):
        expression = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expression)
        expression = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expression)
        expression = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expression)
        try:
            expr = sp.sympify(expression)
            variables = list(expr.free_symbols)
            if len(variables) == 1:
                var = variables[0]
                min_val = float(input(f"Enter the minimum value for {var}: "))
                max_val = float(input(f"Enter the maximum value for {var}: "))
                x_vals = np.linspace(min_val, max_val, 100)
                y_vals = sp.lambdify(var, expr)(x_vals)
                plt.figure(figsize=(8, 6))
                plt.plot(x_vals, y_vals)
                plt.xlabel(str(var))
                plt.ylabel('y')
                plt.title('Graph of ' + str(expr))
                plt.grid(True)
                plt.show()
            elif len(variables) == 2:
                var1, var2 = variables
                min_val1 = float(input(f"Enter the minimum value for {var1}: "))
                max_val1 = float(input(f"Enter the maximum value for {var1}: "))
                min_val2 = float(input(f"Enter the minimum value for {var2}: "))
                max_val2 = float(input(f"Enter the maximum value for {var2}: "))
                x_vals = np.linspace(min_val1, max_val1, 100)
                y_vals = np.linspace(min_val2, max_val2, 100)
                X, Y = np.meshgrid(x_vals, y_vals)
                Z = sp.lambdify((var1, var2), expr)(X, Y)
                fig = plt.figure(figsize=(8, 6))
                ax = fig.add_subplot(111, projection='3d')
                ax.plot_surface(X, Y, Z)
                ax.set_xlabel(str(var1))
                ax.set_ylabel(str(var2))
                ax.set_zlabel('z')
                plt.title('3D Graph of ' + str(expr))
                plt.show()
            else:
                return "The expression must contain one or two variables for graphing."
            return "Graph plotted successfully."
        except sp.SympifyError:
            return "Invalid mathematical expression."

    def finite_series_sum(self, series_type, a, n, r=None):
        if series_type =='arithmetic':
            return (n/2) * (2*a+(n-1)*r)
        elif series_type =='geometric':
            return (a*(1-r**n))/(1-r)
        else:
            raise ValueError(f"only arithmetic and geometric are currently supported. {series_type}")

    def statistics(self, operation, data):
        import statistics
        data = [float(x) for x in data.split(',')]
        if operation == 'mean':
            return statistics.mean(data)
        elif operation =='median':
            return statistics.median(data)
        elif operation =='mode':
            return statistics.mode(data)
        elif operation =='stdev':
            return statistics.stdev(data)
        elif operation == 'variance':
            return statistics.variance(data)
        else:
            raise ValueError (f"Unsupported statistical operation: {operation}")
        
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
            if operation == 'statistics':
                return func(args[0], args[1])  # Pass operation and data as separate arguments
            elif operation == 'finite series sum':
                if len(args) == 3:
                    return func(args[0], float(args[1]), int(args[2]))  # Arithmetic series
                elif len(args) == 4:
                    return func(args[0], float(args[1]), int(args[2]), float(args[3]))  # Geometric series
                else:
                    raise ValueError("Invalid number of arguments for finite series sum")
            else:
                return func(*args)
        else:
            raise ValueError(f"Unsupported math operation: {user_input}")