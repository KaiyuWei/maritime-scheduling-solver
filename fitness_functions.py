# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 11:47:16 2022

@author: kaiyu.wei
"""
import numpy as np

def total_cost(problem):
    """
    calculate the total cost of all vessels

    Parameters
    ----------
    problem : TYPE  vessel_allocation_problem object
        DESCRIPTION.

    Returns
    -------
    sum : TYPE  float
        DESCRIPTION.  the total cost of all the vessels
    """
    total_cost = 0.0   
    for v in problem.vessels:  
        total_cost += (v.real_leaving_time - v.arrival) * v.cost
    return total_cost
        
def complete_time(problem):
    """
    calculate the complete time for all the operation work

    Parameters
    ----------
    problem : TYPE  vessel_allocation_problem object
        DESCRIPTION.

    Returns
    -------
    TYPE  int 
        DESCRIPTION.  the general complete time

    """
    times = []  # list for store work complete times of each berth
    for b in problem.berths:
        if len(b.schedule):  # if the berth still have available time slots
            times.append(b.schedule[-1][0])  # the start time of the last available slots 
                                             # is the work complete time
        else: # if the berth has no time slots, its schedule list is empty
            times.append(b.close)  # the berths closing time                                                     
    return np.amax(times)  # the latest complete time is the general complete time
    
        