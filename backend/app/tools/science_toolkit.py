from scipy import constants
import pint 

# Initialize Unit Registry from pint
ureg = pint.UnitRegistry()

def convert_units(input_string: str) -> str:
    """
    Converts a value between units using the pint library.
    Input should be a string containing the value with its unit
    and the target unit, often separated by 'to' or a comma.
    Examples: '10 meters to feet', '5 kg, pounds', '25 miles/hour to km/h'
    """
    input_string = input_string.strip().strip("'\"()") # Clean up potential LLM quoting/parens
    print(f"Attempting to convert units from input: '{input_string}'")
    parts = []
    if ' to ' in input_string.lower():
        parts = input_string.lower().split(' to ', 1)
    elif ',' in input_string:
        # Split only on the last comma if multiple exist? Or first? Assume last for now.
        last_comma_index = input_string.rfind(',')
        if last_comma_index != -1:
             parts = [input_string[:last_comma_index].strip(), input_string[last_comma_index+1:].strip()]

    value_with_unit_str = None
    target_unit_str = None

    if len(parts) == 2:
        value_with_unit_str = parts[0].strip()
        target_unit_str = parts[1].strip()

    try:
        if not value_with_unit_str or not target_unit_str:
            return f"Error: Could not parse input '{input_string}'. Please provide input like 'value unit to target_unit' or 'value unit, target_unit'."
        print(f"Attempting pint conversion: '{value_with_unit_str}' -> '{target_unit_str}'")
        value_with_unit = ureg(value_with_unit_str) # Let pint parse value and unit
        target_unit = ureg(target_unit_str) # Let pint parse target unit

            # Perform the conversion
        converted_value = value_with_unit.to(target_unit)

            # Format the result nicely
            # Use ~P for pretty formatting including unit
        return f"{value_with_unit_str} is equal to {converted_value:~P}"
    except pint.errors.UndefinedUnitError as e:
        return f"Error: Unknown unit in conversion - {e}"
    except pint.errors.DimensionalityError as e:
        return f"Error: Cannot convert between incompatible units - {e}"
    except Exception as e:
            # Catch other potential parsing errors from pint or general issues
        return f"Error processing unit conversion input '{input_string}': {e}"
    else:
        # Handle cases where parsing failed
        return f"Error: Could not parse input '{input_string}'. Please provide input like 'value unit to target_unit' or 'value unit, target_unit'."
        
def get_physical_constant(constant_name: str) -> str:
    """
    Retrieves the value and unit of a physical constant from SciPy.
    Input 'constant_name' should be a known constant like 'speed of light', 'Planck constant', 'electron mass'.
    """
    print(f"Attempting to retrieve constant: {constant_name}")
    try:
        # SciPy constants are tuples: (value, unit, uncertainty)
        value, unit, _ = constants.physical_constants[constant_name.strip()]
        return f"The value of {constant_name} is {value} {unit}"
    except KeyError:
        print(f"Error retrieving constant: '{constant_name}' not found.")
        # Suggest similar constants? Maybe too complex for now.
        available = list(constants.physical_constants.keys())[:10] # Show a few examples
        return f"Error: Constant '{constant_name}' not found. Available examples: {', '.join(available)}..."
    except Exception as e:
        print(f"Unexpected error retrieving constant '{constant_name}': {e}")
        return f"An unexpected error occurred while retrieving the constant: {e}"


