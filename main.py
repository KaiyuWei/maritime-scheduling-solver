# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 11:27:20 2022

@author: kaiyu.wei
"""
from vessel_allocation_problem import vessel_allocation_problem
from solving_functions import fcfs, pareto_local_search, alloc_by_time_window_size, local_search, tabu_search, simulated_annealing
import os
from copy import deepcopy as dc
import matplotlib.pyplot as plt
import numpy as np



os.chdir("C:/courses/transportation&logistic management/assignment 2/Scenarios-2")
problem = vessel_allocation_problem.from_file("scenario01.txt")  # change dataset here

# # problem 0a 
# problem = fcfs(problem)
# problem.print_solution()


# problem 0b
problem = alloc_by_time_window_size(problem)
problem.print_solution()
pr = dc(problem)  # generally we use this to construct an initial solution because it has some randomness


# # problem 1
# # local_search
# problem1 = local_search(problem, 30000) 
# problem1.print_solution()

# sa_sol = simulated_annealing(problem, max_iters=30000)

# # tabu search
# problem2 = tabu_search(problem, 500)
# problem2.print_solution()

# # problem 2
# front = pareto_local_search(problem, 100)

#problem 4
from sim_heuristic import simulation_cost
max_iteration = 50000  # iteration time for each algorithm
# generate some solutions by different method
local_search_sol = local_search(problem, max_iteration)
tabu_search_sol = tabu_search(problem, max_iteration)
sa_sol = simulated_annealing(problem, max_iters=max_iteration)
solutions = [local_search_sol, tabu_search_sol, sa_sol]
# start simulation of the solutions
num_simu = 100
simu_result = []  # a list of the simulation result, dim: num_solutions x num_simulations
print("...simulation...")
for s in solutions:
    solution_cost = []
    for _ in range(num_simu):
        cost = simulation_cost(s)
        solution_cost.append(cost)  # add the simulation result to the list
    simu_result.append(solution_cost)  # add the results for the solution to the list

fig = plt.figure(figsize =(10, 8)) 
# Creating axes instance
ax = fig.add_axes([0, 0, 1, 1])
# plt.plot([1, 2, 3, 4], [100, 120, 120, 104]) 
# Creating plot
bp = ax.boxplot(simu_result)
# x-axis labels
ax.set_xticklabels(['local search', 'tabu search','simulated annealing']) 
# plot the line that connects average values
average = [np.mean(x) for x in simu_result]
x_axis = [i for i in range(1, len(simu_result) + 1)]
plt.plot(x_axis, average)
plt.title("risk analysis of solutions")
# show plot
plt.show()


        
        
    
    



