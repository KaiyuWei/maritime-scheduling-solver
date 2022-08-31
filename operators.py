# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 14:59:23 2022

@author: kaiyu.wei
"""
import numpy as np
import copy

def swap_between_berths(problem):
    """
    randomly swap two vessels from two berths

    """
    orig = copy.deepcopy(problem)  # store the old problem   
    swap_count = 1  # the time for which we want to try to swap if it fails 
    while (swap_count <= 10):  # try swap at most 10 times
        problem = copy.deepcopy(orig)
        selc_berths = np.random.choice(problem.berths, size=2, replace=False)  # select 2 berths
        if (selc_berths[0].vessels and selc_berths[1].vessels):
            selc_v0 = np.random.choice(selc_berths[0].vessels) 
            selc_v1 = np.random.choice(selc_berths[1].vessels)
            sq0, sq1 = problem.swap_between_berths(selc_v0, selc_v1)
            swap_count += 1  # try at most 10 times
            if (not sq0 and not sq1):
                return problem  # return the swapped vessels           
            else:  # if there are squeezed out vessels, randomly assign them to any berths in the problem
                if sq0:
                    for v in sq0:                       
                        try_count = 1
                        while (try_count <= 10 and not v.is_allocated):
                            b = np.random.choice(problem.berths)  # randomly select a berth
                            index, start_time = b.first_feasible_start_time(v)
                            if index != -1:
                                b.insert_vessel(v, index)
                            try_count += 1
                    # check if all vessels in the squeezed out list have been allocated
                    all_allocated0 = True
                    for v in sq0:
                        if not v.is_allocated:
                            all_allocated0 = False
                            break
                if sq1:
                    for v in sq1:
                        try_count = 1
                        while (try_count <= 10 and not v.is_allocated):
                            b = np.random.choice(problem.berths)  # randomly select a berth
                            index, start_time = b.first_feasible_start_time(v)
                            if index != -1:
                                b.insert_vessel(v, index)
                            try_count += 1
                    # check if all vessels in the squeezed out list have been allocated
                    all_allocated1 = True
                    for v in sq1:
                        if not v.is_allocated:
                            all_allocated1 = False
                            break                   
    if (all_allocated0 and all_allocated1):
        # if all vessels are allocated, return the new solution
        return problem                        
    else:                  
        return orig  # if swap fails, return the original problem
            
def move_in_berth(problem):   
    """
    randomly move one vessel within its own berth

    """
    orig = copy.deepcopy(problem)
    try_count = 1
    while (try_count <= 10):  # try move at most 10 times
        sqz = []
        problem = copy.deepcopy(orig)
        selc_berth = np.random.choice(problem.berths)  # randomly choose a berth
        if (len(selc_berth.vessels) >= 2):  # if the list has at least 2 vessels
            selc_vessels = np.random.choice(selc_berth.vessels, 
                                          size=2, replace=False)  # randomly choose 2 vessels in the list
            # try to move the second one before the first
            selc_berth.remove_vessel(selc_vessels[1])  # first remove the selected vessel that is going to be inserted
            before_ind = selc_berth.vessel_index(selc_vessels[0].id)  # get the insertion index
            sqz = selc_berth.insert_vessel(selc_vessels[1], before_ind)
        try_count += 1
        if (not sqz):  # if sqz is empty, so that the insertion has succeeded
            return problem  # terminate the function, otherwise go back the the while loop
        else:  # if there are squeezed out vessels, randomly assign them to any berths in the problem
            for v in sqz:                       
                try_count = 1
                while (try_count <= 10 and not v.is_allocated):  # try to randomly alocated the vessel, at most 10 times
                    b = np.random.choice(problem.berths)  # randomly select a berth
                    index, start_time = b.first_feasible_start_time(v)
                    if index != -1:
                        b.insert_vessel(v, index)
                    try_count += 1
            # check if all vessels in the squeezed out list have been allocated
            all_allocated = True
            for v in sqz:
                if not v.is_allocated:  
                    all_allocated = False  # if any vessel is not allocated
                    break
    if all_allocated:  # if all vessels are allocated
        return problem  # return the new solution (the neighbor)
    else:
        return orig  # if cannot find a new neighbor, return the original solution
