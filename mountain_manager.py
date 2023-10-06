"""
Mountain Manager class. Provides function to manage mountains on a trail. 
"""
from __future__ import annotations
__author__ = "Haru Le"
from mountain import Mountain

from mountain_organiser import MountainOrganiser
from double_key_table import DoubleKeyTable

class MountainManager:
    """
    Mountain Manager.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    def __init__(self) -> None:
        """ Initialise Mountain Manager. """
        # Dict with Key1: Diff level Key2: Mtn Name Value: Mtn Object
        self.dictionary = DoubleKeyTable()
        self.dictionary.hash1 = lambda k: k % self.dictionary.table_size
        self.mountain_organiser = MountainOrganiser()

    def add_mountain(self, mountain: Mountain) -> None:
        """ 
        Add a mountain to the Mountain Manager. 

        :mountain: Mountain object to be added.
        
        :complexity: O(add_mountain()) -> O(Mlog(M) + N)
        Where M is the length of input list and N is the total number of mountains so far.
        """
        self.mountain_organiser.add_mountains([mountain])
        self.dictionary[(mountain.difficulty_level, mountain.name)] = mountain

    def remove_mountain(self, mountain: Mountain) -> None:
        """ 
        Remove a mountain from the Mountain Manager. 

        :mountain: Mountain object to be removed.
        
        :complexity: O(remove_mountain())
        ->
        :complexity best: O(1)
        :complexity worst: O(n)
        Where n is the number of mountains in the organiser.
        """
        self.mountain_organiser.remove_mountain(mountain)
        self.dictionary.__delitem__((mountain.difficulty_level, mountain.name))

    def edit_mountain(self, old: Mountain, new: Mountain) -> None:
        """ 
        Edit a mountain in the Mountain Manager. 

        :old: Old Mountain object to be edited.
        :new: New Mountain object to be replace old.
        
        :complexity: O(remove_mountain() + add_mountain()) -> O(Mlog(M) + N)
        Where M is the length of input list and N is the total number of mountains so far.
        """
        self.remove_mountain(old)
        self.add_mountain(new)

    def mountains_with_difficulty(self, diff: int) -> list[Mountain]:
        """ 
        Return list of mountains of difficulty - diff. 

        :diff: Specified mountain difficulty to return.
        
        :complexity: O(1)
        """
        # This is how to do it if you don't care about name order, and want the most efficient function.
        try:
            return self.dictionary.values(diff)
        except KeyError:
            return []
        # This is how to do it if you want to return a list of diff levels, sorted lexiocraphically.
        # O(n) Where n is the number of mountains in the organiser.
        # mountains = self.mountain_organiser.organiser
        # res = []
        # for mtn in mountains:
        #     if mtn.difficulty_level == diff:
        #         res.append(mtn)
        #     # Makes a bit more efficient
        #     if mtn.difficulty_level > diff:
        #         break
        # return res

    def group_by_difficulty(self) -> list[list[Mountain]]:
        """ 
        Return list of list of mountains of different difficulties. 

        :complexity: O(d)
        Where d is the number of difficulties in the Mountain Manager.
        """
        res = []
        for diff_level in self.dictionary.iter_keys():
            res.append(self.mountains_with_difficulty(diff_level))
        return res
        # This is how to do it if you want it sorted lexiocraphically.
        # O(n^2)
        # mountains = self.mountain_organiser.organiser
        # prev_difficulty_level = None
        # res = []
        # for mtn in mountains:
        #     if mtn.difficulty_level == prev_difficulty_level:
        #         continue
        #     difficulty_level = mtn.difficulty_level
        #     prev_difficulty_level = difficulty_level
        #     res.append(self.mountains_with_difficulty(difficulty_level))
        # return res
