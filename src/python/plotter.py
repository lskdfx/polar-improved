import numpy as np
from sympy import lambdify
from sympy.abc import theta

def transform_solution(solution):
    if solution["solution"] == "standard" and solution["r"] < 0:
        solution["theta"] += np.pi;
        solution["r"] *= -1;
    return solution;

def plot_polar(ax, expr, solutions):
    func1 = lambdify(theta, expr[0], modules="numpy");
    func2 = lambdify(theta, expr[1], modules="numpy");

    space = np.linspace(-2*np.pi, 2*np.pi, 1000);

    range1 = func1(space)
    range2 = func2(space)

    # apply negative transformation. matplotlib doesn't do this?
    space1 = space + (range1 < 0) * np.pi;
    space2 = space + (range2 < 0) * np.pi;
    range1 = np.abs(range1)
    range2 = np.abs(range2)

    ax.plot(space1, range1, label=str(expr[0]));
    ax.plot(space2, range2, label=str(expr[1]));

    for solution in solutions:
        solution = transform_solution(solution);
        if solution["solution"] == "standard":
            ax.plot(solution["theta"], solution["r"], marker="o");
        elif solution["solution"] == "origin":
            ax.plot(0, 0, marker="o");
