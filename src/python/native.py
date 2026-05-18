from equationinput import parse_polar 
from solver import solve_polar_intersections
from plotter import plot_polar

import matplotlib.pyplot as plt

#expr1 = input("expr1 ")
#expr2 = input("expr2 ")
#expr1 = r"2\cos(2*\theta)"
#expr2 = r"\sin(\theta)"
#expr1 = r"3+2\sin{2\theta} + \cos{2\theta}"
#expr2 = r"4\cos{2\theta}"
expr1 = r"\sin(\theta)"
expr2 = r"2\cos(3\theta)"

print(expr1, expr2);
expr = parse_polar(expr1, expr2);
print(expr);

solutions = solve_polar_intersections(expr);

for solution in solutions:
    print(solution)

fig, ax = plt.subplots(subplot_kw={"projection": "polar"});

plot_polar(ax, expr, solutions);

ax.legend();
plt.show();
