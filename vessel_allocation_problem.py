# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 11:36:11 2022

@author: kaiyu.wei
"""
import numpy as np
import copy
import itertools

class vessel_allocation_problem:   
    def __init__(self, vessels, berths):
        """
        Parameters
        ----------
        nr_vessel: int
        nr_berth: int
        vessels : TYPE list of vessels
        berths : TYPE list of berth
            DESCRIPTION.
        """
        self.vessels = vessels
        self.berths = berths
        self.nr_vessel = len(vessels)
        self.nr_berth = len(berths)
    
    @classmethod
    def from_file(cls, filename):
        """
        use data from file to create a problem model
        Parameters
        ----------
        cls : TYPE the class itself
            DESCRIPTION.
        filename : TYPE string
            DESCRIPTION. name of the file from which the data are read

        Returns
        -------
        TYPE problem object
        DESCRIPTION. a problem model
        """
        with open(filename, 'r') as raw_data:
            data = raw_data.read().splitlines()
            nrVes = int(data[0])  # nr of vessels
            nrBer = int(data[1])  # nr of berths
            arrVes = [int(i) for i in data[2].split()]  # arrival time of vessels
            openBer = [int(i) for i in data[3].split()]  # open time of berths
            handling = []
            for i in range(4, 4 + nrVes):
                handling.append([int(j) for j in data[i].split()])  # handling time of each vessel in each berth
            closeBer = [int(i) for i in data[4 + nrVes].split()]  # closing time of berths
            closeVes = [int(i) for i in data[5 + nrVes].split()]  # closing time of vessels
            costVes = [float(i) for i in data[6 + nrVes].split()]  # cost per unit time per vessel
            
            vessels = []
            berths = []
            # create vessels
            for i in range(nrVes):
                v = vessel(arrVes[i], closeVes[i], handling[i], costVes[i])
                
                # check if the vessel is possible to be served
                can_be_served = False
                for j in range(len(v.handling_time)):
                    if v.arrival + v.handling_time[j] <= v.leaving:
                        can_be_served = True
                if can_be_served:   
                    vessels.append(v)
                else:
                    print(f"{v.id} cannot be served by any berth")
                    nrVes -= 1
            # create berths
            for i in range(nrBer):
                berths.append(berth(openBer[i], closeBer[i]))
            return cls(vessels, berths)
    
    def __eq__(self, rhs):
        """
        definition for the equal signe "=="

        Parameters
        ----------
        rhs : TYPE  problem object
            DESCRIPTION.  the object that is used for comparation

        Returns  
        -------
        TYPE  boolean
            DESCRIPTION.  True if two solutions have same schedule, False otherwise

        """
        if (len(self.vessels) == len(rhs.vessels)):
            for i in range(len(self.vessels)):
                rhs_vessel = rhs.get_vessel(self.vessels[i].id)  # the vessel with same id in rhs
                if ((self.vessels[i].berth.id != rhs_vessel.berth.id) 
                    or self.vessels[i].operation_start != rhs_vessel.operation_start):
                    return False  # if any same vessel with different berths or starting time
            return True  # if all the vessels with same id have same berth and starting time              
        else: return False  # if two solutions have different number of vessels
            
    def all_allocated(self):
        """
        for debugging

        Returns
        -------
        None.

        """
        for v in self.vessels:
            if v.is_allocated == False:
                return False, v.id
        return True, -2
    
    def get_berth(self, berthID):
        for b in self.berths:
            if b.id == berthID:
                return b
    
    def get_vessel(self, vesselID):
        for v in self.vessels:
            if v.id == vesselID:
                return v
    
    def print_solution(self):
        print("vessel id\tberth_id\tstar_time\tleaving_time\thandling_time")
        for v in self.vessels:
            if (v.berth):
                print(v.id, "\t", v.berth.id, "\t", v.operation_start, 
                      "\t", v.real_leaving_time, "\t", v.real_handling_time)
    
    def print_schedules(self):
        print("berth id\tschedule")
        for b in self.berths:
            print(b.id, "\t", b.schedule)
            
    def first_available_berth(self, vessel):
        """
        look for the first available berth for the vessel in vessel id sequence

        Parameters
        ----------
        vessel : TYPE vessel object
            DESCRIPTION. the vessel that is looking for an available berth

        Returns
        -------
        first_berth : TYPE berth object
            DESCRIPTION. the first available berth to the vessel
                    none if available berth not found
        start_time : TYPE the possible operation starting time of the vessel
                    -1 if available berth 
            DESCRIPTION.

        """
        start_time = -1
        
        for b in self.berths:
            start_time, slot_ind = b.first_available_slot(vessel)
            if start_time != 500:
                return b, start_time
        return None, start_time  # if no available berth, return none and -1
    
    def nearest_available_berth(self, vessel):
        """
        find out the time window among all berths for the vessel, that makes the operation
        to start as early as possible. 

        Parameters
        ----------
        vessel : TYPE vessel object
            DESCRIPTION.  the vessel that needs to be allocated

        Returns
        -------
        TYPE berth object
            DESCRIPTION.  the berth that allows the vessel to start its oepration asap
        TYPE start time, int
            DESCRIPTION. the operation start time
        """
        first_berth = None
        start_times = []  
        for i in range(len(self.berths)):  # loop over berths
            op, slot_ind = self.berths[i].first_available_slot(vessel)
            start_times.append(op)
        
        first_berth = self.berths[np.argmin(start_times)]  # select the earliest start time
        start_time = np.amin(start_times)  
        if start_time != 500:
            return first_berth, start_time
        else: 
            return None, -1  # if no berth found 
    
    def swap_between_berths(self, v0, v1):
        """
        swap two vessels between their berths

        Parameters
        ----------
        v0 : TYPE vessel object 0
        v1 : TYPE vessel object 1

        Returns
        -------
        squeeze0 : TYPE list of vessel
            DESCRIPTION.  if any vessel is squeezed out and so the swap fails, the squeezed out 
                vessel from berth 0 would be in the list and be returned
        squeeze1 : TYPE list of vessel
            squeeze0 : TYPE list of vessel
            DESCRIPTION.  if any vessel is squeezed out and so the swap fails, the squeezed out 
                vessel from berth 1 would be in the list and be returned
        """
        
        
        
        b0 = v0.berth
        ind0 = b0.vessel_index(v0.id)  # v0's index in the list
        b1 = v1.berth
        ind1 = b1.vessel_index(v1.id)  # v1's index in teh list
        
        # remove berths
        b0.remove_vessel(v0)
        b1.remove_vessel(v1)
        # find suiteble start time for the vessel
        squeeze0 = b0.insert_vessel(v1, ind0)
        squeeze1 = b1.insert_vessel(v0, ind1)
        return squeeze0, squeeze1
        
            
    def vessel_index(self, vessel_id):
        """
        search vessel by id and return the index in the vessels list of the problem

        Parameters
        ----------
        vessel_id : TYPE string
            DESCRIPTION. the vessel's id

        Returns
        -------
        i : TYPE int
            DESCRIPTION. the index of the vessel in the list

        """
        for i in range(len(self.vessels)):
            if self.vessels[i].id == vessel_id:
                return i
     
    def reset(self):
        """
        remove all vessels from all berths

        """
        for b in self.berths:
            num_vessels = len(b.vessels)
            for i in range(num_vessels):
                b.remove_vessel(b.vessels[0])  # always remove the first one in the list, 
                                               # since its size changes    
                                               
    def debug(self):
        for v in self.vessels:
            if not v.berth:
                return 0
            return 1
    
class vessel:
    new_id = itertools.count().__next__
    def __init__(self, arrival, leaving, handling_time, cost):
        """
        Parameters
        ----------
        arrival : TYPE int
            DESCRIPTION. arrival time of the vessel
        leaving : TYPE int 
            DESCRIPTION.  leaving time of the vessel
        handling_time : TYPE array of int, length = nr of berths
            DESCRIPTION. the handling time the vessel need on each berth
        cost : TYPE float
            DESCRIPTION. the cost of the vessel per unit time
        """
        self.id = f'vessel_{vessel.new_id()}'
        self.arrival = arrival  # arrival time of the time window
        self.leaving = leaving  # leaving time of the time window
        self.handling_time = handling_time  # list of handling time in each berth
        self.cost = cost  # cost per unit time
        self.berth = None  # the berth in which the vessel is allocated
        self.operation_start = 500  # Initialize with a very late impossible operation start time
        self.real_handling_time = 200  # the certain handling time after the vessel is allocated to a berth
        self.real_leaving_time = 700  # the certain leaving time after the vessel is allocated to a berth
        self.is_allocated = False  # a bool value indicating if a vessel has been allocated
    
    def reset(self):
        self.berth = None
        self.operation_start = None  
        self.real_handling_time = None 
        self.real_leaving_time = None
        self.is_allocated = False
        
        
class berth:
    new_id = itertools.count().__next__
    def __init__(self, start, close):
        
        """
        Parameters
        ----------
        start : TYPE int
            DESCRIPTION. start time of the berth
        close : TYPE int
            DESCRIPTION. close time of the berth
        """
        self.id = f'berth_{berth.new_id()}'
        self.start = start
        self.close = close
        self.schedule = [[start, close]]  # list of available time slots, 
                                # initialized by schedule for an empty berth
        self.vessels = []  # the list of vessels 
        
    def add_vessel(self, vessel, start_time):
        """
        add a vessel to the berth in a suitable time slot
        Parameters
        ----------
        vessel : TYPE vessel object
            DESCRIPTION. the vessel that is allocated to the berth
        start_time : TYPE int
            DESCRIPTION. the vessel's operation start time

        Returns
        ------
        type vessel object if not added
            DESCRIPTION.  if the vessel  is not added it will be returned 
        """
        if (not self.is_vessel_in(vessel)): 
            slot_ind = self.to_slot_ind(start_time)
            if (start_time + vessel.handling_time[int(self.id[6:])] <= self.schedule[slot_ind][1]
                and start_time + vessel.handling_time[int(self.id[6:])] <= vessel.leaving):
                self.vessels.append(vessel)
                vessel.berth = self  # set the berth attribute of the vessel
                vessel.operation_start = start_time  # set the attribute value for the vessel
                vessel.real_handling_time = vessel.handling_time[int(self.id[6:])]
                vessel.real_leaving_time = vessel.operation_start + vessel.real_handling_time
                vessel.is_allocated = True
                self.calc_slot(slot_ind, start_time, vessel.real_handling_time)     
            else:
                #print(f"Cannot add! {vessel.id} violates the time constraint")
                return vessel                
        else:
            print(f"Cannot add! {vessel.id} is already in {self.id}")
            return vessel
        
    def may_insert(self, inserted, index):
        """
        check whether a vessel can be inserted in the index

        Parameters
        ----------
        inserted : TYPE  vessel object 
            DESCRIPTION. vessel that is going to be inserted
        index : TYPE int
            DESCRIPTION. the index to which the vessel is inserted

        Returns
        -------
        TYPE  boolean
            DESCRIPTION. if the vessel can be inserted, return True; False otherwise


        """
        op_start = 0
        if (index >= len(self.vessels)):  # if the vessel is inserted in the last place
            op_start = max(inserted.arrival, self.vessels[-1].real_leaving_time)
            real_leaving = op_start + inserted.handling_time[int(self.id[6:])]
            if (real_leaving > self.close or real_leaving > inserted.leaving):
                return False
            else:
                return True
        elif index <= 0:
            index = 0
            op_start = max(self.start, inserted.arrival)  
        else:  # if index is in the range(len(self.vessels))
            op_start = max(self.vessels[index - 1].real_leaving_time, inserted.arrival)          
        pre_leaving = op_start + inserted.handling_time[int(self.id[6:])]  # leaving time of the previous vessel
        for i in range(index, len(self.vessels)):
            # calculate whether the violate the time constrant one by one if insert the vessel
            v = self.vessels[i]  # the vessel in the list
            op_start = max(pre_leaving, v.arrival)  # update the operation start time
            pre_leaving = op_start + v.handling_time[int(self.id[6:])]
            if pre_leaving > v.leaving:
                return False # if any violation of the time constraint
        if pre_leaving > self.close:
            return False  # if the last vessel leave later than the closing time of the berth
        else:
            return True
            
    def remove_vessel(self, vessel):
        """
        remove vessel from the berth, and reschedule all vessels behind the removed vesssel

        Parameters
        ----------
        vessel : TYPE vessel object
            DESCRIPTION. the vessel that is going to be removed 

        Raises
        ------
        Exception
            DESCRIPTION. if the vessel is not in the berth, raise the exception
        
        Returns
        -------
        TYPE vessel object
            DESCRIPTION.  the removed vessel
        """

        if (self.is_vessel_in(vessel)):
            remove_ind = self.vessel_index(vessel.id)
            sublist = self.vessels[remove_ind:]
            # first remove all vessels in the sublist
            for i in range(len(sublist)):
                self.vessels.remove(sublist[i])
                self.restore_schedule(sublist[i])  # recalculate the schedule after remove the vessel
            if (len(sublist) > 1):
                # add back vessels except the vessel that we want to remove   
                op_start = max(self.schedule[-1][0], sublist[1].arrival) 
                for i in range(1, len(sublist)):   
                    self.add_vessel(sublist[i], op_start)
                    if (i != len(sublist) - 1):              
                        op_start = max(sublist[i].real_leaving_time, 
                                       sublist[i+1].arrival)  # update operation starting time for next vessel            
            # update the removed vessel's attributes
            vessel.reset()
            return vessel  # return the removed vessel                
        else:
            raise Exception(f"Cannot remove! {vessel.id} is not in {self.id}")
    
    def insert_vessel(self, inserted, before_ind):
        """
        insert a vessel in the middle of the berths schedule and recalculate the vessels' schedule
        after the insertion place.
        if there's any vessel does not fit for the time window, it will be returned in a list.

        Parameters
        ----------
        inserted : TYPE vessel object
            DESCRIPTION. the vessel that is going to be inserted
        before_ind : TYPE int
            DESCRIPTION. the vessel index before which the inserted vessel is inserted

        Raises
        ------
        Exception 
            DESCRIPTION. 1. if the before_which is not in the berth
                            2. is the inserted vessel is in other berth

        Returns
        -------
        squeezed_out_vessels : TYPE list of vessels
            DESCRIPTION. if any vessel cannot fit the time window, it will be returned 
                            in the list

        """
        squeezed_out = []  # for storing the vessels that cannot fit the schedule after the insertion
        if (before_ind >= len(self.vessels)):
            if (not inserted.is_allocated):
                target_slot = self.schedule[-1]  # the last time slot of the berth
                start_time = max(inserted.arrival, target_slot[0])
                not_added = self.add_vessel(inserted, start_time)  # if the index out of range, add the vessel to the end of the list
                if not_added:
                    not_added.reset()
                    squeezed_out.append(not_added)  # if not added return it in the list
                    return squeezed_out
            else:
                raise Exception(f"Cannot insert! {inserted.id} is in {inserted.berth.id}")  
        else:
            before_which = self.vessels[before_ind]  # the vessel before which the insertion should be
            if (self.is_vessel_in(before_which) and not inserted.is_allocated):
                before_ind =  self.vessel_index(before_which.id)
                sublist = self.vessels[before_ind:] 
                # first remove all vessels in the sublist
                for i in range(len(sublist)):
                    self.vessels.remove(sublist[i])
                    self.restore_schedule(sublist[i])  # recalculate the schedule after remove the vessel
                # add back vessels including the vessel that is to be inserted
                sublist.insert(0, inserted)  # insert the inserted vessel to the first place of the list
                op_start = max(self.schedule[-1][0], sublist[0].arrival)  # calculate the earlist start time
                for i in range(len(sublist)):
                    handling = sublist[i].handling_time[int(self.id[6:])]
                    leaving = sublist[i].leaving
                    if (op_start + handling <= leaving
                        and op_start + handling <= self.close):  # check if the time still fit for the vessel
                        self.add_vessel(sublist[i], op_start)     
                        if (i != len(sublist) - 1):
                            op_start = max(sublist[i].real_leaving_time, 
                                           sublist[i+1].arrival)  # update operation starting time for next vessel                                      
                    else:
                        # update the squeezed out vessel's attributes
                        sublist[i].reset()   
                        squeezed_out.append(sublist[i])  # if a vessel is not fit for the schedule
                return squeezed_out  # return the squeezed out list      
            elif not self.is_vessel_in(before_which):
                raise Exception(f"Cannot insert! {before_which.id} is not in {self.id}")
            else:
                raise Exception(f"Cannot insert! {inserted.id} is in {inserted.berth.id}")
                
    
    def is_vessel_in(self, vessel):
        """
        check if a vessel is allocated in the berth

        Parameters
        ----------
        vessel : TYPE vessel object

        Returns
        -------
        TYPE bool
            DESCRIPTION. if the input vessel is in the berth, returns True; 
                otherwise, False.
        """
        return vessel in self.vessels
    
    def print_vessels(self):
        """
        print vessel information in the berth
        """
        print("vessel_id\ttw.start\toper.start\ttw.end\toper.end\thandling_time")
        for v in self.vessels:
            print(v.id, " ", v.arrival, " ", v.operation_start, " ", 
                      v.leaving, " ", v.real_leaving_time, " ",  v.real_handling_time)
    
    def to_slot_ind(self, start_time):
        """
        search for the time slot in the schedule with the start_time and return the index

        Parameters
        ----------
        start_time : TYPE int
            DESCRIPTION. start time of the time slot 
            
        Returns
        -------
        slot_ind : TYPE int
            DESCRIPTION. the index of the time slot which the start time is in.

        """
        slot_ind = None
        for i in range(len(self.schedule)):
            if (self.schedule[i][0] <= start_time 
                and self.schedule[i][1] > start_time):
                slot_ind = i
                break
        if (slot_ind != -1):
            return slot_ind
        else:
            # if the time slot is not available
            return -1
   
    def vessel_index(self, vessel_id):
        """
        search vessel by id and return the index in the vessels list of the berth

        Parameters
        ----------
        vessel_id : TYPE string
            DESCRIPTION. the vessel's id

        Returns
        -------
        i : TYPE int
            DESCRIPTION. the index of the vessel in the list

        """
        for i in range(len(self.vessels)):
            if self.vessels[i].id == vessel_id:
                return i
            
    def first_feasible_start_time(self, vessel):
        """
        find the first available start time for the vessel

        Parameters
        ----------
        vessel : TYPE vessel object
            DESCRIPTION.  the vessel that is looking for an available start time

        Returns
        -------
        TYPE int
            DESCRIPTION. the index to which the vessel can be inserted, -1 if not found
        op_start : TYPE  int
            DESCRIPTION. the start time for the operation, 500 if not found

        """
        if self.schedule:
            for i in range(len(self.vessels)):
                if self.may_insert(vessel, i):
                    op_start = max(vessel.arrival, self.start)
                    if i != 0:
                        op_start = max(vessel.arrival, 
                                       self.vessels[i-1].real_leaving_time)               
                    return i, op_start
            last_slot = self.schedule[-1]  # check if the last time slot in the schedule list 
            arrival = vessel.arrival
            op_start = max(arrival, last_slot[0])
            leaving = vessel.leaving
            handling = vessel.handling_time[int(self.id[6:])]
            if op_start + handling <= min(leaving, last_slot[1], self.close):
                return len(self.vessels), op_start
            else:   return -1, 500
                
                
    def first_available_slot(self, vessel):
        """
        find out the first available start time and slot in the current berth, given a vessel

        Parameters
        ----------
        vessel : TYPE vessel object
            DESCRIPTION.  the vessel that is looking for a time slot in the berth

        Returns
        -------
        TYPE int, int
            DESCRIPTION. 1. returns the earliest staring time in this berth for the vessel
                    2. returns the index of the first available slot in the berth
        """
        arrival_time = vessel.arrival
        schedule = self.schedule
        handling = vessel.handling_time[int(self.id[6:])]        
        if (handling == 200):               
            return 500, -1  # if current berth is not allowed, return a very late start time and slot int -1    
        elif (len(schedule)):  # if the schedule list is not empty                
            for j in range(len(schedule)):
                tw = schedule[j]  # the time window
                op = max(arrival_time, tw[0])  # if vessel is in the slot, the opeartion start time
                if (op + handling <= tw[1]
                    and op + handling <= vessel.leaving): 
                    # the operation should be ended before the end of the time window
                    # as well as the vessel's leaving time
                    return op, j        
            return 500, -1  # if no available slot found, return large start time and index -1
    
    def calc_slot(self, slot_ind, start_time, handling_time):
        """
        recalculate the schecule when a vessel is allocated in the berth
        
        Parameters
        ----------
        slot_ind : TYPE int
            DESCRIPTION. the index of slot in the berth's schedule
        start_time : TYPE int
            DESCRIPTION. the start time of the vessel's operator
        handling_time : TYPE int
            DESCRIPTION. the duration that the vessel's operation takes

        Raises
        ------
        Exception
            DESCRIPTION. if the vessel's start time and handling time doesn't fit 
                the selected time window
        """
        if (start_time >= self.schedule[slot_ind][0] 
            and start_time + handling_time <= self.schedule[slot_ind][1]):
            select_slot = self.schedule[slot_ind]  # the time slot into which the vessel is assigned
            insert_slot = [[select_slot[0], start_time], 
                           [start_time + handling_time, select_slot[1]]]
            for s in insert_slot:
                if s[0] != s[1]:  # if the slot length is not 0
                    self.schedule.insert(0, s)
            self.schedule.remove(select_slot)
            self.schedule.sort()  # sort the list by the start time of slots
        else:  
            # if the vessel's starting or handling time does not match the selected slot
            raise Exception(f"Impossible to allocate this vessel into time window {slot_ind} of {self.id}")
    
    def restore_schedule(self, vessel):
        """
        calculate the schedule of the berth when a vessel is removed from it

        Parameters
        ----------
        vessel : TYPE  vessel object
            DESCRIPTION.  the vessel that is removed from the berth
        """
        start = vessel.operation_start  # the operation start time
        end = vessel.real_leaving_time  # the operation end time
        self.schedule.insert(0, [start, end])
        self.schedule.sort()  # sort the schedule list according to starting time
        ind_new = self.to_slot_ind(start)  # the index of the newly added time slot
        
        if (ind_new != 0 
            and self.schedule[ind_new - 1][1] == start):
            # if the new slot is not the first slot and it has no gap with its previous slot
            prev = self.schedule[ind_new - 1]  # the previous time slot
            merged = [prev[0], end]  # merged slot with the previous one
            self.schedule.remove(prev)  # remove previous time slot
            self.schedule.remove([start, end])  # remove the newly added time slot
            self.schedule.insert(0, merged)  # insert the the merged time slot
            start = merged[0]  # update the start time of the newly added time slot
            end = merged[1]  # update the end time of the newly added time slot
            self.schedule.sort()  # sort the schedule by the starting time
            ind_new -= 1  # update the index of the newly added slot
       
        if (ind_new != len(self.schedule) - 1 
            and self.schedule[ind_new + 1][0] == end):
            # if the slot is not the last time slot and it has no gap with the next slot
            next = self.schedule[ind_new + 1]  # the next time slot
            merged = [start, next[1]]  # the merged time slot
            self.schedule.remove(next)
            self.schedule.remove([start, end])
            self.schedule.insert(0, merged)
            self.schedule.sort()  # sort the schedule by the starting time
        