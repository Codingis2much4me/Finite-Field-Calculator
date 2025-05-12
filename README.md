# Field Emulator – Finite Field Calculator GUI

## Overview  
This project provides a desktop GUI application to explore finite fields 𝔽(pᵐ).  
- Enter a prime *p* and degree *m*.  
- Supply an irreducible polynomial of degree *m* over 𝔽ₚ.  
- View a list of all field elements, their representations, and generate multiplication and inverse tables.  
- Perform field arithmetic expressions with a calculator-like interface.

## Assumptions  
- Input prime *p* is small enough that primality testing by trial division is acceptable (usually *p* ≤ 10⁶).  
- Irreducible polynomial degree *m* is small (≤ 3) for a conclusive irreducibility check; higher degrees rely on user verification.  
- Field size *pᵐ* remains manageable in memory (typically ≤ 10⁴ elements).  
- Polynomial strings use the format `c x^i` joined by `+`, e.g. `1+x+x^3`. No subtraction operator in input—negative coefficients are handled modulo *p*.  
- The GUI runs on a system where Tkinter is available (standard in Python 3.x distributions).

## Features  
- Polynomial addition, subtraction, multiplication, and modular reduction.  
- Irreducibility check for degrees 1–3; warning for higher degrees.  
- Generation of all *pᵐ* field elements.  
- Multiplication table viewer with scrolling.  
- Expression evaluator supporting `+`, `–`, `*`, `/` and parentheses.  
- Interactive GUI built with Tkinter (scrolled text, ttk).

## Prerequisites  
- Python 3.6+  

## Installation  
1. Clone the repository:  
   ```sh
   git clone <your-repo-url>
   cd <repo-directory>
   ```  

## Usage  
```sh
python cs425proj_mod.py
```  
1. Enter **Prime p** and **Degree m**.  
2. Type an **irreducible polynomial** (e.g. `1+x+x^3`).  
3. Click **Initialize Field**.  
4. View elements, generate multiplication table via **Tools → View Multiplication Table**, or check irreducibility.  
5. Build or type expressions and click **Evaluate Expression**.

## Project Structure  
- **cs425proj_mod.py** – Main application.  
  - `poly_add`, `poly_sub`, `poly_mul`, `poly_mod` – basic polynomial ops.  
  - `is_prime`, `is_irreducible` – primality and irreducibility tests.  
  - `generate_field_elements`, `build_mul_table`, `build_inv_table`.  
  - `parse_poly`, `poly_str` – parser and pretty-printer.  
  - `evaluate_expression` – shunting-yard-based evaluator using lookup tables.  
  - GUI code: frames for input, elements, operators, and output.  
