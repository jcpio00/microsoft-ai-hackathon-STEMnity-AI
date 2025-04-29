
import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from sympy.solvers import solve
from sympy import SympifyError, Symbol

# Define transformations for parsing user input safely
transformations = (standard_transformations + (implicit_multiplication_application,))

def solve_algebraic_equation(equation_str: str) -> str:
    """
    Solves basic algebraic equations for a single variable (usually 'x').
    Input should be a string like 'x + 5 = 10' or '2*x - 4 = 0'.
    """
    print(f"Attempting to solve equation: {equation_str}")
    try:
        # Assume the variable is 'x' unless specified otherwise
        x = Symbol('x')
        
        # Split equation into LHS and RHS
        if '=' not in equation_str:
            return "Error: Invalid equation format. Please include '=' sign."
        
        lhs_str, rhs_str = equation_str.split('=', 1)
        
        # Parse the expressions safely
        lhs = parse_expr(lhs_str.strip(), transformations=transformations, local_dict={'x': x})
        rhs = parse_expr(rhs_str.strip(), transformations=transformations, local_dict={'x': x})
        
        # Create the equation object
        equation = sympy.Eq(lhs, rhs)
        
        # Solve the equation
        solution = solve(equation, x)
        
        if not solution:
            return "Could not find a solution for the equation."
        else:
            # Format solution nicely
            if isinstance(solution, list):
                 # Handle multiple solutions if necessary, e.g., quadratic
                 solution_str = ", ".join([str(s) for s in solution])
                 return f"The solution(s) for x are: {solution_str}"
            else:
                 return f"The solution is: x = {solution}"
            
    except (SympifyError, TypeError, ValueError) as e:
        print(f"Error solving equation '{equation_str}': {e}")
        return f"Error: Could not parse or solve the equation '{equation_str}'. Please check the format. Error: {e}"
    except Exception as e:
        print(f"Unexpected error solving equation '{equation_str}': {e}")
        return f"An unexpected error occurred while solving: {e}"

def factor_expression(expression_str: str) -> str:
    """
    Factors a given mathematical expression.
    Input should be a string like 'x**2 - 4' or 'a**2 + 2*a*b + b**2'.
    """
    print(f"Attempting to factor expression: {expression_str}")
    try:
        # Parse the expression safely
        # Allow common variables like x, y, z, a, b, c by default
        local_dict = {var: Symbol(var) for var in 'xyzabc'}
        expr = parse_expr(expression_str.strip(), transformations=transformations, local_dict=local_dict)
        
        # Factor the expression
        factored_expr = sympy.factor(expr)
        
        if factored_expr == expr: # Check if factoring actually changed anything
             return f"The expression '{expression_str}' could not be factored further."
        else:
             return f"The factored form of '{expression_str}' is: {factored_expr}"
             
    except (SympifyError, TypeError, ValueError) as e:
        print(f"Error factoring expression '{expression_str}': {e}")
        return f"Error: Could not parse or factor the expression '{expression_str}'. Please check the format. Error: {e}"
    except Exception as e:
        print(f"Unexpected error factoring expression '{expression_str}': {e}")
        return f"An unexpected error occurred while factoring: {e}"


