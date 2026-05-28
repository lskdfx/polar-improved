from eqninput import parse_polar
from solver import polar_get_info

from sympy import Interval, pi
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
domain = Interval(0, 2*pi)
print(expr);

info = polar_get_info(expr, domain);

for solution in info["solutions"]:
    print(solution)

fig, ax = plt.subplots(subplot_kw={"projection": "polar"});

ax.plot(info["expr1"][0], info["expr1"][1], label=str(expr[0]));
ax.plot(info["expr2"][0], info["expr2"][1], label=str(expr[1]));

for solution in info["solutions"]:
    if solution["solution"] == "standard":
        ax.plot(solution["theta"], solution["r"], marker="o");
    elif solution["solution"] == "origin":
        ax.plot(0, 0, marker="o");

ax.legend();
plt.show();
