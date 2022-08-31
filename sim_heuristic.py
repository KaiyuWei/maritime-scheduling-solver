# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 14:41:28 2022

@author: kaiyu.wei
"""
import numpy as np

def simulation_cost(problem):
    """
    evaluate the input solution and return the cost in a circumstance of stochastic 
    arrival time and handling time.

    """
    berth_cost = []  # a list of costs for each berth
    for b in problem.berths:
        vessel_cost = .0
        allowed_start = b.start
        for v in b.vessels:
            r_arrival = np.random.randint(v.arrival + 2, v.arrival + 5)  # real arrival time
            static_handling = v.handling_time[int(b.id[6:])]  
            r_start = max(allowed_start, r_arrival)  # real start time for operation considering the real arrival time
            r_handling = np.random.randint(static_handling + 1, static_handling + 7)  # real handling time
            r_leaving = r_start + r_handling  # real leaving time
            normal_cost = (r_leaving - r_arrival) * v.cost  # cost for handling operation
            delay_cost = 25.0 * (r_start - v.operation_start) if r_start > v.operation_start else 0  # cost for delay
            late_punishment = 450 if r_leaving > v.leaving else 0
            vessel_cost += (normal_cost + delay_cost + late_punishment)  # add cost of the current vessel
            # update the earlist start time for the next vessel
            allowed_start = r_leaving
        berth_cost.append(vessel_cost)  # add the cost of the berth to the cost list
    return np.sum(berth_cost)
            

                
            
            
        
