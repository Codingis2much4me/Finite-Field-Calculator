"""
Authors: 2203117(Maanas Bhaya), 2203112(Harshit Goyal), 2203302(Aditya Sehra)
Project: Field Emulator
This project demonstrates a GUI for a field emulator. We take an input for the degree m and the prime p and give a list of all the irreducible polynomials to the user.
The user is then presented with a calculator-like interface giving them operations to perform in the Field modulo the irreducible polynomial they have entered.
"""

import itertools
import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import ttk # Import ttk for themed widgets like scrollbar

# Polynomial operations
def poly_add(a, b, p):
    res = [(x + y) % p for x, y in itertools.zip_longest(a, b, fillvalue=0)]
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res

def poly_sub(a, b, p):
    res = [(x - y) % p for x, y in itertools.zip_longest(a, b, fillvalue=0)]
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res

def poly_mul(a, b, p):
    res = [0] * (len(a) + len(b) - 1)
    for i in range(len(a)):
        for j in range(len(b)):
            res[i + j] = (res[i + j] + a[i] * b[j]) % p
    return res

def poly_mod(poly, mod_poly, p):
    poly = poly[:]
    while len(poly) >= len(mod_poly):
        if poly[-1] == 0:
            poly.pop()
            continue
        factor = poly[-1]
        for i in range(len(mod_poly)):
            poly[len(poly) - len(mod_poly) + i] -= factor * mod_poly[i]
            poly[len(poly) - len(mod_poly) + i] %= p
        while poly and poly[-1] == 0:
            poly.pop()
    return poly

# Check if a number is prime
def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

# Check if a polynomial is irreducible
def is_irreducible(poly, p):
    degree = len(poly) - 1
    if degree <= 0:
        return False
    
    # For degree 1, any polynomial ax + b (a≠0) is irreducible
    if degree == 1:
        return poly[1] != 0
    
    # For degree 2 and 3, check if there are any linear factors
    if degree in [2, 3]:
        # Check if polynomial is divisible by any linear polynomial (x - a)
        for a in range(p):
            divisor = [a, 1]  # x - a as [a, 1]
            if len(poly_mod(poly.copy(), divisor, p)) == 0:
                return False
        return True
    
    return "Cannot conclusively verify irreducibility for degrees > 3"

# Generate all elements of the field
def generate_field_elements(p, m):
    return [list(coeffs) for coeffs in itertools.product(range(p), repeat=m)]

# Build multiplication table
def build_mul_table(elements, mod_poly, p):
    table = {}
    for a in elements:
        for b in elements:
            prod = poly_mod(poly_mul(a, b, p), mod_poly, p)
            prod_tuple = tuple(prod + [0] * (len(a) - len(prod)))
            table[(tuple(a), tuple(b))] = prod_tuple
    return table

# Build inverse table
def build_inv_table(elements, mul_table):
    identity = tuple([1] + [0] * (len(elements[0]) - 1))
    inv_table = {}
    for a in elements:
        a_tuple = tuple(a)
        for b in elements:
            if mul_table.get((a_tuple, tuple(b))) == identity:
                inv_table[a_tuple] = tuple(b)
                break
    return inv_table

# Pretty print polynomial
def poly_str(poly):
    terms = []
    for i, c in enumerate(poly):
        if c == 0:
            continue
        if i == 0:
            terms.append(f"{c}")
        elif i == 1:
            if c == 1:
                terms.append("x")
            else:
                terms.append(f"{c}x")
        else:
            if c == 1:
                terms.append(f"x^{i}")
            else:
                terms.append(f"{c}x^{i}")
    return ' + '.join(terms) if terms else "0"

# Parse polynomial string like "1+x+x^2"
def parse_poly(s, p, m=None):
    s = s.replace(" ", "")
    terms = s.split("+")
    max_deg = 0
    coeffs = {}
    for term in terms:
        if "x^" in term:
            c, i = term.split("x^")
            c = int(c) if c else 1
            i = int(i)
        elif "x" in term:
            c = term.replace("x", "")
            c = int(c) if c else 1
            i = 1
        else:
            c = int(term)
            i = 0
        coeffs[i] = coeffs.get(i, 0) + c % p
        max_deg = max(max_deg, i)

    size = m if m else max_deg + 1
    result = [0] * size
    for i, c in coeffs.items():
        if i < size:
            result[i] = c % p
    return result

# Evaluate expression in the field
def evaluate_expression(expr, p, m, mul_table, inv_table):
    tokens = []
    i = 0
    expr = expr.replace(" ", "")
    
    while i < len(expr):
        if expr[i] in '()+-*/':
            tokens.append(expr[i])
            i += 1
        elif expr[i].isdigit() or expr[i] == 'x':
            # Extract polynomial term
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == 'x' or expr[j] == '^'):
                j += 1
            tokens.append(expr[i:j])
            i = j
        else:
            i += 1
    
    output = []
    ops = []

    def precedence(op):
        return {'+': 1, '-': 1, '*': 2, '/': 2}.get(op, 0)

    def apply_op(op):
        b = output.pop()
        a = output.pop()
        
        # Convert to lists for operations if they're tuples
        a_list = list(a) if isinstance(a, tuple) else a
        b_list = list(b) if isinstance(b, tuple) else b
        
        if op == '+':
            res = tuple(poly_add(a_list, b_list, p))
        elif op == '-':
            res = tuple(poly_sub(a_list, b_list, p))
        elif op == '*':
            res = mul_table.get((a, b))
            if res is None:
                # Try converting to proper length tuples if lookup fails
                a_tuple = tuple(a_list + [0] * (m - len(a_list)))
                b_tuple = tuple(b_list + [0] * (m - len(b_list)))
                res = mul_table.get((a_tuple, b_tuple))
        elif op == '/':
            if b not in inv_table:
                # Make sure b is properly formatted for inverse lookup
                b_tuple = tuple(b_list + [0] * (m - len(b_list)))
                inv_b = inv_table.get(b_tuple)
                if inv_b is None:
                    raise ValueError(f"No inverse exists for {poly_str(b_list)}")
            else:
                inv_b = inv_table[b]
                
            res = mul_table.get((a, inv_b))
            if res is None:
                a_tuple = tuple(a_list + [0] * (m - len(a_list)))
                res = mul_table.get((a_tuple, inv_b))
                
        output.append(res)

    for token in tokens:
        if token in "+-*/":
            while ops and ops[-1] != '(' and precedence(ops[-1]) >= precedence(token):
                apply_op(ops.pop())
            ops.append(token)
        elif token == '(':
            ops.append(token)
        elif token == ')':
            while ops and ops[-1] != '(':
                apply_op(ops.pop())
            if ops and ops[-1] == '(':
                ops.pop()  # Remove the left parenthesis
        else:
            poly_coeffs = parse_poly(token, p, m)
            # Ensure consistent tuple length for lookups
            padded_tuple = tuple(poly_coeffs + [0] * (m - len(poly_coeffs)))
            output.append(padded_tuple)

    while ops:
        apply_op(ops.pop())

    return list(output[0])






















# GUI functions and variables
current_p = None
current_m = None
current_mod_poly = None
current_elements = None
current_mul_table = None
current_inv_table = None
element_buttons = []  # To store references to element buttons

# Function to add a character to the expression entry
def add_to_expr(char):
    current_pos = entry_expr.index(tk.INSERT)
    entry_expr.insert(current_pos, char)
    entry_expr.focus_set()

# Function to add a field element to the expression
def add_element_to_expr(element):
    element_str = poly_str(element)
    current_pos = entry_expr.index(tk.INSERT)
    entry_expr.insert(current_pos, element_str)
    entry_expr.focus_set()

# Clear the expression
def clear_expr():
    entry_expr.delete(0, tk.END)
    entry_expr.focus_set()

# Function to show multiplication table
def show_multiplication_table():
    if current_elements is None:
        messagebox.showerror("Field Not Initialized", "Please initialize the field first!")
        return
    
    # Create a new window for the multiplication table
    table_window = tk.Toplevel(root)
    table_window.title(f"Multiplication Table for F({current_p}^{current_m})")
    table_window.geometry("800x600")
    
    # Create a frame with scrollbars for the table
    frame = tk.Frame(table_window)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create scrollbars
    v_scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
    h_scrollbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
    
    # Create canvas with scrollbars
    canvas = tk.Canvas(frame, yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    v_scrollbar.config(command=canvas.yview)
    h_scrollbar.config(command=canvas.xview)
    
    # Pack scrollbars and canvas
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Create a frame inside the canvas to hold the table
    table_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=table_frame, anchor=tk.NW)
    
    # Add table headers - first cell is empty
    tk.Label(table_frame, text="", width=8, relief=tk.RIDGE, padx=5, pady=5).grid(row=0, column=0)
    
    # Add column headers (field elements)
    for col, element in enumerate(current_elements, 1):
        tk.Label(table_frame, text=poly_str(element), width=8, relief=tk.RIDGE, 
                 bg='lightgray', padx=5, pady=5).grid(row=0, column=col)
    
    # Add row headers and fill the table
    for row, a in enumerate(current_elements, 1):
        # Row header
        tk.Label(table_frame, text=poly_str(a), width=8, relief=tk.RIDGE,
                 bg='lightgray', padx=5, pady=5).grid(row=row, column=0)
        
        # Table cells
        for col, b in enumerate(current_elements, 1):
            prod = list(current_mul_table[(tuple(a), tuple(b))])
            tk.Label(table_frame, text=poly_str(prod), width=8, relief=tk.RIDGE,
                     padx=5, pady=5).grid(row=row, column=col)
    
    # Update canvas scroll region
    table_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# Function to check if a polynomial is irreducible over the field
def check_irreducibility():
    try:
        p = int(entry_p.get())
        if not is_prime(p):
            messagebox.showerror("Error", f"{p} is not a prime number!")
            return
        
        poly_str_input = entry_poly.get()
        poly = parse_poly(poly_str_input, p)
        
        irreducible_result = is_irreducible(poly, p)
        if isinstance(irreducible_result, str):
            messagebox.showinfo("Irreducibility Check", irreducible_result)
        elif irreducible_result:
            messagebox.showinfo("Irreducibility Check", f"The polynomial {poly_str_input} is irreducible over F{p}.")
        else:
            messagebox.showerror("Irreducibility Check", f"The polynomial {poly_str_input} is NOT irreducible over F{p}.")
    except Exception as e:
        messagebox.showerror("Error", f"Error checking irreducibility: {e}")

def initialize_field():
    global current_p, current_m, current_mod_poly, current_elements, current_mul_table, current_inv_table, element_buttons
    
    # Clear any existing element buttons
    for button in element_buttons:
        button.destroy()
    element_buttons = []
    
    try:
        current_p = int(entry_p.get())
        current_m = int(entry_m.get())
        
        # Validate p is prime
        if not is_prime(current_p):
            messagebox.showerror("Input Error", f"{current_p} is not a prime number!")
            return
            
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid integer values for p and m.")
        return

    poly_str_input = entry_poly.get()
    try:
        current_mod_poly = parse_poly(poly_str_input, current_p, current_m + 1)
        
        # Show the irreducible polynomial in a nicer format
        irreducible_poly_str = poly_str(current_mod_poly)
        field_info.config(state=tk.NORMAL)
        field_info.delete("1.0", tk.END)
        field_info.insert(tk.END, f"Field: F({current_p}^{current_m})\n")
        field_info.insert(tk.END, f"Irreducible Polynomial: {irreducible_poly_str}\n")
        field_info.insert(tk.END, f"Field Order: {current_p**current_m} elements\n")
        field_info.config(state=tk.DISABLED)
        
    except Exception as e:
        messagebox.showerror("Polynomial Error", f"Error parsing polynomial: {e}")
        return

    # Check if the polynomial is irreducible
    irreducible_result = is_irreducible(current_mod_poly, current_p)
    if isinstance(irreducible_result, str):
        messagebox.showwarning("Irreducibility Warning", 
                               f"{irreducible_result}\nContinuing initialization, but please verify your polynomial is irreducible.")
    elif not irreducible_result:
        messagebox.showerror("Irreducibility Error", 
                             f"The polynomial {poly_str_input} is NOT irreducible over F{current_p}. Field initialization aborted.")
        return

    current_elements = generate_field_elements(current_p, current_m)
    current_mul_table = build_mul_table(current_elements, current_mod_poly, current_p)
    current_inv_table = build_inv_table(current_elements, current_mul_table)

    # Display field elements
    text_field_elements.delete("1.0", tk.END)
    text_field_elements.insert(tk.END, "Field Elements:\n")
    for e in current_elements:
        text_field_elements.insert(tk.END, f"{poly_str(e)}  ->  {tuple(e)}\n")
    
    # Create buttons for field elements
    button_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Calculate how many elements per row based on the number of elements
    total_elements = len(current_elements)
    elements_per_row = min(8, total_elements)  # Maximum 8 per row
    
    # Create buttons for each field element
    for i, element in enumerate(current_elements):
        row = i // elements_per_row
        col = i % elements_per_row
        element_str = poly_str(element)
        btn = tk.Button(button_frame, text=element_str, 
                        command=lambda e=element: add_element_to_expr(e),
                        width=8, height=1)
        btn.grid(row=row, column=col, padx=2, pady=2)
        element_buttons.append(btn)
    
    # Show operator buttons
    operator_frame.pack(fill=tk.X, padx=10, pady=5)
    
    messagebox.showinfo("Field Initialization", "Field has been initialized successfully!")

def evaluate_expr():
    if current_p is None or current_m is None or current_mod_poly is None:
        messagebox.showerror("Field Not Initialized", "Please initialize the field first!")
        return
    expr = entry_expr.get()
    try:
        result = evaluate_expression(expr, current_p, current_m, current_mul_table, current_inv_table)
        output = f"Result: {poly_str(result)}  ->  {tuple(result)}"
        text_result.config(state=tk.NORMAL)
        text_result.delete("1.0", tk.END)
        text_result.insert(tk.END, output)
        text_result.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror("Evaluation Error", f"Error evaluating expression: {e}")

# GUI Layout
root = tk.Tk()
root.title("Finite Field Calculator for F(p^m)")
root.geometry("800x700")  # Set initial window size

# --- Create a Canvas and a Scrollbar for the main window ---
canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas) # This frame will hold all the content

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Pack the canvas and scrollbar
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
# --- End of Scrollbar setup ---


# Add a menubar
menubar = tk.Menu(root)
tools_menu = tk.Menu(menubar, tearoff=0)
tools_menu.add_command(label="View Multiplication Table", command=show_multiplication_table)
tools_menu.add_command(label="Check Irreducibility", command=check_irreducibility)
menubar.add_cascade(label="Tools", menu=tools_menu)
root.config(menu=menubar)

# Main frame with border and padding - Now placed inside the scrollable_frame
# Remove relief and borderwidth as it's inside the canvas now
main_frame = tk.Frame(scrollable_frame, padx=15, pady=15)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10) # Pack inside scrollable_frame

# Field initialization frame - Now a child of main_frame
frame_field = tk.LabelFrame(main_frame, text="Field Initialization", padx=10, pady=10)
frame_field.pack(fill=tk.X)

# Two-column layout for p and m
input_frame = tk.Frame(frame_field)
input_frame.pack(fill=tk.X, pady=5)

tk.Label(input_frame, text="Prime p:").grid(row=0, column=0, sticky=tk.W)
entry_p = tk.Entry(input_frame, width=8)
entry_p.grid(row=0, column=1, padx=5, pady=2)

tk.Label(input_frame, text="Degree m:").grid(row=0, column=2, sticky=tk.W, padx=(20,0))
entry_m = tk.Entry(input_frame, width=8)
entry_m.grid(row=0, column=3, padx=5, pady=2)

# Polynomial input
tk.Label(frame_field, text="Irreducible polynomial:").pack(anchor=tk.W, pady=(5,0))
entry_poly = tk.Entry(frame_field, width=40)
entry_poly.pack(fill=tk.X, padx=5, pady=2)

# Initialize button
btn_init = tk.Button(frame_field, text="Initialize Field", command=initialize_field, bg="#4CAF50", fg="white")
btn_init.pack(pady=5)

# Field information display
field_info = tk.Text(frame_field, height=3, wrap=tk.WORD, state=tk.DISABLED)
field_info.pack(fill=tk.X, pady=5)

# Field elements display
frame_elements = tk.LabelFrame(main_frame, text="Field Elements", padx=10, pady=10)
frame_elements.pack(fill=tk.BOTH, expand=True, pady=5)
text_field_elements = scrolledtext.ScrolledText(frame_elements, wrap=tk.WORD, height=8)
text_field_elements.pack(fill=tk.BOTH, expand=True)

# Button frame for field elements (will be populated after initialization)
button_frame = tk.Frame(main_frame)
# Not packing yet - will be packed after field initialization

# Operator buttons
operator_frame = tk.Frame(main_frame)
# Not packing yet - will be packed after field initialization

# Add operator buttons
op_buttons = [
    ('+', lambda: add_to_expr('+')),
    ('-', lambda: add_to_expr('-')),
    ('*', lambda: add_to_expr('*')),
    ('/', lambda: add_to_expr('/')),
    ('(', lambda: add_to_expr('(')),
    (')', lambda: add_to_expr(')')),
    ('x', lambda: add_to_expr('x')),
    ('Clear', clear_expr)
]

for i, (op, cmd) in enumerate(op_buttons):
    btn = tk.Button(operator_frame, text=op, command=cmd, width=5, height=1)
    if op == 'Clear':
        btn.config(bg="#f44336", fg="white")  # Red for Clear
    elif op in '+-*/':
        btn.config(bg="#2196F3", fg="white")  # Blue for operators
    else:
        btn.config(bg="#9E9E9E", fg="white")  # Gray for other symbols
    btn.grid(row=i//4, column=i%4, padx=5, pady=2)

# Expression input and evaluation
frame_expr = tk.LabelFrame(main_frame, text="Expression Evaluation", padx=10, pady=10)
frame_expr.pack(fill=tk.X, pady=5)

tk.Label(frame_expr, text="Enter or build expression:").pack(anchor=tk.W)
entry_expr = tk.Entry(frame_expr, width=60)
entry_expr.pack(fill=tk.X, padx=5, pady=5)

btn_eval = tk.Button(frame_expr, text="Evaluate Expression", command=evaluate_expr,
                     bg="#FF9800", fg="white", height=2)
btn_eval.pack(pady=5, fill=tk.X)

# Result display
frame_result = tk.LabelFrame(main_frame, text="Result", padx=10, pady=10)
frame_result.pack(fill=tk.X, pady=5)
text_result = tk.Text(frame_result, height=2, wrap=tk.WORD, state=tk.DISABLED)
text_result.pack(fill=tk.X, padx=5, pady=2)

# Add some instructions at the bottom
instructions = tk.Label(main_frame, text="Instructions: First initialize the field, then use the calculator buttons or type directly. Use the Tools menu for additional functions.",
                       anchor=tk.W, justify=tk.LEFT, wraplength=750)
instructions.pack(fill=tk.X, pady=10)

root.mainloop()