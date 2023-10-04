from __future__ import annotations

from mountain import Mountain

from double_key_table import DoubleKeyTable

from infinite_hash_table import InfiniteHashTable

from data_structures.hash_table import LinearProbeTable
from algorithms.binary_search import binary_search
from algorithms.mergesort import mergesort, merge

class MountainOrganiser:
    """
    Mountain Organiser.
    Implementation Facts:
    - Infinite Hash Table should be used to sort lexicographically
    """
    def __init__(self) -> None:
        # Dictionary
        self.dictionary = LinearProbeTable()
        # Actual organised list
        self.organiser = list()

    def cur_position(self, mountain: Mountain) -> int:
        """
        Finds the rank of the provided mountain given all mountains included so far. 
        :raises KeyError: If this mountain hasn't been added yet.
        :comp: O(log(N)), where N is the total number of mountains so far.
        """
        # if self.dictionary.__contains__[mountain.name]:
            # log(N) comes from binary search
        return self.dictionary[mountain.name]

    def add_mountains(self, mountains: list[Mountain]) -> None:
        """
        :comp: O(Mlog(M) + N), M length of input list, N total number of mountains so far.
        """
        # Hash table is to count how many mtns in diff level. 
        counts_hash_table = LinearProbeTable()
        counts_hash_table.hash = lambda k: k % counts_hash_table.table_size
        # Mlog(M) complexity comes from using merge sort to sort the input list
        # Then it would be M to add it to the original list, but that cancels out.
        # N complexity comes from merging the whole list back together again.

        # O(Mlog(M))
        sorted_mountains = mergesort(mountains, lambda x:x.difficulty_level)
        # O(N)
        self.organiser = merge(self.organiser, sorted_mountains, lambda x:x.difficulty_level)
        for mtn in self.organiser:
            print(mtn.difficulty_level, mtn.name)
        # So now everything is sorted by difficulty level
        # We should go through the whole list again and sort lexicographically
        # O(N)
        for mtn in self.organiser:
            key = mtn.difficulty_level
            try:
                counts_hash_table[key] += 1
            except:
                counts_hash_table[key] = 1
        
        # This should also be O(N)
        # Use an iterator? Might lessen complexity
        print(counts_hash_table)
        for diff_level in counts_hash_table.keys():
            names = InfiniteHashTable()
            if counts_hash_table[diff_level] > 1:
                for rank, mtn in enumerate(self.organiser):
                    if mtn.difficulty_level == diff_level:
                        print(rank, mtn.name)
                        names[mtn.name] = (mtn, rank)
            if len(names) > 0:
                sorted_names = names.sort_keys()
                for x, name in enumerate(sorted_names):
                    mtn_info = names[name]
                    mtn_object, index = mtn_info
                    if x == 0:
                        lowest_rank = index
                    else:
                        lowest_rank += 1
                    self.organiser[lowest_rank] = mtn_object
        
        for rank, mtn in enumerate(self.organiser):
            self.dictionary[mtn.name] = rank

    def binary_search(self, mtn_list, mtn) -> int:
        """
        Utilise the binary search algorithm to find the index where a particular element would be stored.

        :return: The index at which either:
            * This item is located, or
            * Where this item would be inserted to preserve the ordering.

        :complexity:
        Best Case Complexity: O(1), when middle index contains item.
        Worst Case Complexity: O(log(N)), where N is the length of l.
        """
        return self._binary_search_aux(mtn_list, mtn, 0, len(mtn_list))

    def _binary_search_aux(self, mtn_list, mtn, lo: int, hi: int) -> int:
        """
        Auxilliary method used by binary search.
        lo: smallest index where the return value could be.
        hi: largest index where the return value could be.
        """
        if lo == hi:
            return lo
        mid = (hi + lo) // 2
        if mtn_list[mid].difficulty_level > mtn.difficulty_level:
            # Item would be before mid
            return self._binary_search_aux(mtn_list, mtn, lo, mid)
        elif mtn_list[mid].difficulty_level < mtn.difficulty_level:
            # Item would be after mid
            return self._binary_search_aux(mtn_list, mtn, mid+1, hi)
        elif mtn_list[mid].difficulty_level == mtn.difficulty_level:
            return mid
        raise ValueError(f"Comparison operator poorly implemented {mtn} and {mtn_list[mid]} cannot be compared.")