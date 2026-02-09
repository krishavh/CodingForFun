#!/usr/bin/env python3
"""
Quick symbolic integration example using SymPy.
Integrates sin(x) with respect to x.
"""

import sympy as sp


def main() -> None:
    x = sp.symbols("x")
    expr = sp.sin(x)
    integral = sp.integrate(expr, x)
    print(f"Integral of {expr} dx = {integral} + C")


if __name__ == "__main__":
    main()
