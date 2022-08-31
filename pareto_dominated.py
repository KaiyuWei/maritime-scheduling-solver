# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 10:41:17 2022

@author: kaiyu.wei
"""
from fitness_functions import total_cost, complete_time

def not_dominated(solu1, solu2):
    """
    determine whether the solu2 is dominates by solu1

    Parameters
    ----------
    exist_solu : TYPE  existing solution (problem object)
    new_solu : TYPE  newly generated solution

    Returns
    -------
    TYPE  bool 
        DESCRIPTION. True if new solution dominates the existing solution 
                        (so the new one should be in the Pareto front list )
                    False otherwise
    """
    cost1 = total_cost(solu1)
    cost2 = total_cost(solu2)
    time1 = complete_time(solu1)
    time2 = complete_time(solu2)
    if (cost2 <= cost1 and time2 <= time1):
        return True  # solu2 is not dominated by solu1
    else: 
        return False
    

    