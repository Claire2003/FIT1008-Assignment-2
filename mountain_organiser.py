"""
Mountain Organiser class. A class that sorts mountains and stores their information.
"""
from __future__ import annotations
__author__ = "Haru Le"

from mountain import Mountain

from infinite_hash_table import InfiniteHashTable

from data_structures.hash_table import LinearProbeTable

from algorithms.mergesort import mergesort, merge

class MountainOrganiser:
    """
    Mountain Organiser.

    Unless stated otherwise, all methods have O(1) complexity.
    """
    def __init__(self) -> None:
        """ Initialise Mountain Organiser. """
        # Hash table of mtns and rank. Key: mtn name Value: Rank
        self.hash_table = LinearProbeTable()
        # Actual organised list of mountains
        self.organiser = []

    def cur_position(self, mountain: Mountain) -> int:
        """
        Finds the rank of the provided mountain given all mountains included so far. 

        :mountain: Search mountain. 

        :raises KeyError: If this mountain hasn't been added yet.

        :complexity: O(1)
        """
        return self.hash_table[mountain.name]

    def add_mountains(self, mountains: list[Mountain]) -> None:
        """
        Adds a list of mountains to the organiser.

        :mountains: List of mountains to be added to organiser.

        :complexity: O(Mlog(M) + N)
        Where M is the length of input list and N is the total number of mountains so far.
        """
        # Counts hash table is to count how many mtns in each diff level. 
        counts_hash_table = LinearProbeTable()
        counts_hash_table.hash = lambda k: k % counts_hash_table.table_size
        # O(Mlog(M))
        # Sort before adding. 
        sorted_mountains = mergesort(mountains, lambda x:x.difficulty_level)
        # O(M+N) (This cancels out in the grand scheme of things)
        # Because input is already sorted, we can use mergesorts merge method which is M+N comp to combine the two sorted lists.
        self.organiser = merge(self.organiser, sorted_mountains, lambda x:x.difficulty_level)
        # So now everything is sorted by difficulty level
        # We should go through the whole list again and sort lexicographically
        # O(M+N)
        for mtn in self.organiser:
            key = mtn.difficulty_level
            try:
                # Key exists
                counts_hash_table[key] += 1
            except:
                # Key doesnt exist
                counts_hash_table[key] = 1
        
        # O(M+N), goes over all elements in organiser. 
        # Only if there are multiple mtns under the same diff level, 
        # Do we sort lexicographically. 
        # Doesn't become n^2 complexity as the greater there are under 1 diff level
        # The less there will be under another diff level.
        for diff_level in counts_hash_table.keys():
            names = InfiniteHashTable()
            if counts_hash_table[diff_level] > 1:
                for rank, mtn in enumerate(self.organiser):
                    if mtn.difficulty_level == diff_level:
                        names[mtn.name] = (mtn, rank)
            if len(names) > 0:
                # Sort names
                sorted_names = names.sort_keys()
                # Use their sorted index to rank them in the organiser.
                for sorted_index, name in enumerate(sorted_names):
                    mtn_info = names[name]
                    mtn_object, index = mtn_info
                    if sorted_index == 0:
                        lowest_rank = index
                    else:
                        lowest_rank += 1
                    self.organiser[lowest_rank] = mtn_object
        # Add to hash table for cur position method. 
        # O(M+N)
        for rank, mtn in enumerate(self.organiser):
            self.hash_table[mtn.name] = rank
        
    def remove_mountain(self, mountain: Mountain) -> None:
        """
        Remove a mountain from the organiser.

        :mountain: Mountain to be removed.
        
        :complexity best: O(1)
        :complexity worst: O(n)
        Where n is the number of mountains in the organiser.
        Best case: Remove the highest rank mountain. No need to shuffle. Or change higher ranks in hash table.
        Worst case: Remove the lowest rank mountain. Shuffle all elements to the left one, change all remaining mtns rank in hash table.
        """
        # Get sublist from ahead of it.
        remove_position = self.cur_position(mountain)
        sub_list = self.organiser[remove_position+1:] # O(length of slice) < O(n)
        # Remove from list
        # Complexity of remove in python list is O(n), as it shuffles all elements on the right to the left one. 
        self.organiser.remove(mountain) 
        # Remove from dict O(1)
        self.hash_table.__delitem__(mountain.name)
        # O(n)
        for mtn in sub_list:
            # Decrement rank.
            self.hash_table[mtn.name] -= 1