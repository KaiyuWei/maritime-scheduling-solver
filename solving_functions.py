# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 20:55:08 2022

@author: kaiyu.wei
"""
import numpy as np
import copy
from operators import swap_between_berths, move_in_berth
from fitness_functions import total_cost, complete_time
import matplotlib.pyplot as plt

operators = [swap_between_berths, move_in_berth]

def fcfs(problem):
    """
    generate a soluiton by first come first serve rule. Allocate vessels to the earliest available
    berth.
    assume that all vessels in the problem has not been allocated. If there's any, use problem.reset()
    to remove all allocations.

    Parameters
    ----------
    problem : TYPE vessel_allocation_problem object
        DESCRIPTION.  initial solution

    Raises
    ------
    Exception  
        DESCRIPTION. if any vessel cannot find an available berth, raise the exceptioni

    Returns
    -------
    problem : TYPE vessel_allocation_problem object
        DESCRIPTION.  solution

    """
    vessels = problem.vessels  # list of vessels
    vessels.sort(key=lambda x : x.arrival)  # sort vessle according to arrival time ascendingly
    vessel_ind = 0
    while (vessel_ind < len(problem.vessels)):
        # when there are still vessels not considered, continue the while loop
        to_ber, start_time = problem.nearest_available_berth(vessels[vessel_ind])  # find the nearest available berth
        if to_ber is not None:
            to_ber.add_vessel(vessels[vessel_ind], start_time)  # add the vessel to the first available berth                      
            vessel_ind += 1;            
        else:
            raise Exception(f"fcfs failed, {vessels[vessel_ind].id} cannot find an available berth")
    vessels.sort(key=lambda x : int(x.id[7:]))
    return problem

def alloc_by_time_window_size(problem):
    """
    allocate the vessels by their time window size (from larger to smaller time window)

    Parameters
    ----------
    problem : TYPE problem object

    Raises
    ------
    Exception
        DESCRIPTION. if the allocation fails

    Returns
    -------
    problem : the problem with allocated vessels
    """  
    orig = copy.deepcopy(problem)
    all_allocated = False
    while (not all_allocated):
        end_vessel_loop = False
        problem = copy.deepcopy(orig)
        vessels = problem.vessels  # list of vessels
        vessels.sort(key=lambda x : (x.leaving - x.arrival), reverse=True)  # sort vessle according to tw size descendingly
        vessel_ind = 0
        while (vessel_ind < len(problem.vessels) and not end_vessel_loop):   
            start_time = 500           
            checklist = copy.deepcopy(problem.berths)
            while (start_time == 500 and len(checklist) != 0):    
                selc_berth = np.random.choice(checklist)
                to_ber = problem.get_berth(selc_berth.id)
                checklist.remove(selc_berth)                    
                start_time, slot_ind = to_ber.first_available_slot(vessels[vessel_ind])              
            if (start_time != 500):                    
                to_ber.add_vessel(vessels[vessel_ind], start_time)
                vessel_ind += 1 
            if (start_time == 500 and not checklist):
                end_vessel_loop = True
        if vessel_ind == len(vessels):
            all_allocated = True
    
    # sort the vessel list of all berths by vessels operation start time
    for b in problem.berths:
        b.vessels.sort(key=lambda x : x.operation_start)
               
    vessels.sort(key=lambda x : int(x.id[7:]))
    return problem

def local_search(problem, max_iter):
    print("...local search...")    
    cur_fit = total_cost(problem)
    cur_problem = copy.deepcopy(problem)
    fit = [cur_fit]
    for _ in range(max_iter):
        f = np.random.choice(operators)
        new_neighbor = f(problem)
        if (new_neighbor.vessels):
            neighbor_fit = total_cost(new_neighbor)
            if neighbor_fit <= cur_fit:
                cur_fit = neighbor_fit
                cur_problem = copy.deepcopy(new_neighbor)
        fit.append(cur_fit)
    plt.plot(fit)
    plt.title("fitness in local search")
    plt.show()
    return cur_problem

def berth_utilization(problem):
    availableTime = []
    berth_utility = []
    for b in problem.berths:
        if len(b.schedule):
            availableTime.append(0)
            for j in b.schedule:
                availableTime[int(b.id[6:])] += (j[1]-j[0])  
        else:
            availableTime.append(0)
        tempval = (b.close - b.start - availableTime[int(b.id[6:])])/int(b.close - b.start)
        berth_utility.append(tempval)
    print(berth_utility)
    return berth_utility
        
def tabu_search(problem, max_iter):
    print("...tabu search...")
    cur_fit = total_cost(problem)  # current fitness 
    cur_problem = copy.deepcopy(problem)  # current solution
    fit = [cur_fit]   # the list for storing the fitnesses as the iteration goes
    tabu_length = 100  # max length of the tabu list
    tabuList = []  
    iter_count = 0  
    while (iter_count <= max_iter):
        f = np.random.choice(operators)
        new_neighbor = f(problem)  
        if (new_neighbor.vessels and (new_neighbor not in tabuList)):  # check if the solution is feasible and if it is in the tabu list
            neighbor_fit = total_cost(new_neighbor)
            if neighbor_fit <= cur_fit:
                cur_fit = neighbor_fit
                cur_problem = copy.deepcopy(new_neighbor)
            tabuList.append(cur_problem)
            if len(tabuList) > tabu_length:
                tabuList = tabuList[-tabu_length:]  # only keep the last "tabu_length" elements in tabu list          
            iter_count += 1  # only update the count when an valid neighbor is found 
        fit.append(cur_fit)       
    plt.plot(fit)
    plt.title("fitness in tabu search")
    plt.show()
    return cur_problem

from pareto_dominated import not_dominated
def pareto_local_search(problem, max_iter):
    print("...pareto local search...")
    explored_list = []  # list for solutions that has been explored
    list_length = 50
    cur_problem = copy.deepcopy(problem)  # current problem
    front = [cur_problem]  # for storing pareto fronts
    iter_count = 0
    
    while(iter_count <= max_iter):
        cur_problem = np.random.choice(front)  # randomly select one solution in the front list
        f = np.random.choice(operators)  # choose an operator
        new_neighbor = f(cur_problem)  # generate a new neighbor 
        if new_neighbor not in explored_list:
            new_dominated = False  # true if the new solution is dominated by any solution in the front
            for solution in front:  # compare the neighbor with all solutions in the front list         
                new_not_domi_by_exist = not_dominated(solution, new_neighbor)  # return true if new is not dominated by the existing solution
                exist_not_domi_by_new = not_dominated(new_neighbor, solution)              
                if not new_not_domi_by_exist:  # if new is dominated by existing solution
                    new_dominated = True  # if new is dominated by any existing one
                    explored_list.append(copy.deepcopy(new_neighbor))  # add new solution to explored list if dominated by any
                elif not exist_not_domi_by_new:  # if existing is dominated by new
                     explored_list.append(solution)  # the existing solution be added to the explored list
                     front.remove(solution)  # remove the existing solution from the front 
            if not new_dominated:    # if new is not dominated by any existing one        
                front.append(copy.deepcopy(new_neighbor)) 
            
            # adjust the explored list if necessary
            no_longer_than = len(explored_list) <= list_length
            while not no_longer_than:
                explored_list.pop(0)  # if longer than max length
                no_longer_than = len(explored_list) <= list_length
            
        iter_count += 1
    return front

def simulated_annealing(problem, initial_temperature=500, end_temperature=1, alpha=0.99, max_iters=1000):
    print("...simulated annealing...")
    current_solution = problem
    current_value = total_cost(problem)
    current_temperature = initial_temperature
    best_solution = copy.deepcopy(current_solution)
    iter_count = 0
    fit = [current_value]
    while (current_temperature >= end_temperature or iter_count <= max_iters):
        f = np.random.choice(operators)  # choose the operator
        candidate_solution = f(problem)
        candidate_value = total_cost(candidate_solution)
        delta = candidate_value - current_value
        acceptance_probability = np.exp(-abs(delta / 10000) / current_temperature)
        if delta <= 0:  # if new neighbor has a lower cost
            current_solution = candidate_solution
            current_value = candidate_value
            if total_cost(best_solution) >= current_value:
                best_solution = copy.deepcopy(current_solution)
        elif acceptance_probability >= np.random.random():
            current_solution = candidate_solution
            current_value = candidate_value
        # update the temperature and iteration count
        current_temperature *= alpha
        iter_count += 1
        fit.append(total_cost(best_solution))
    plt.plot(fit)
    plt.title("simulated annealing")
    plt.show()
    return best_solution

