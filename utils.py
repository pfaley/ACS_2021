"""
This file has various utility functions.
"""

def string_to_int(in_str):
    """
    Filters out all non-numeric characters from the string
    and turns the resulting string into an integer and
    returns it.
    """
    int_vals = filter(lambda x: x.isdigit(), in_str)
    out = int(''.join(int_vals))

    return out

def format_float_list(in_list):
    """
    Formats a list into a more print-friendly format
    """
    return [f'{i:.4f}' if type(i) is float else i for i in in_list]
