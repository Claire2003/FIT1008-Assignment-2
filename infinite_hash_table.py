"""
Infinite Hash Table class. A type of table that can be used to sort strings lexicographically. 
"""
from __future__ import annotations
__author__ = "Haru Le"

from typing import Generic, TypeVar

from data_structures.referential_array import ArrayR

K = TypeVar("K")
V = TypeVar("V")

class InfiniteHashTable(Generic[K, V]):
    """
    Infinite Hash Table.

    Type Arguments:
        - K:    Key Type. In most cases should be string.
                Otherwise `hash` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    TABLE_SIZE = 27

    def __init__(self,level=0) -> None:
        """
        Infinite Hash Table initialisation. 
        :level: Integer with default of 0. Level determines order in the chain, and also pos of letter for hash. 
        """
        self.level = level
        # Count refers to the number of elements in all tables coming from origin, including origin.
        self.count = 0
        # Origin is the table, called origin, because from here other tables may sprout.
        self.origin:ArrayR[tuple[K, V]] = ArrayR(self.TABLE_SIZE)

    def hash(self, key: K) -> int:
        """
        Hash the key for insert/retrieve/update into the hashtable.
        """
        if self.level < len(key):
            return ord(key[self.level]) % (self.TABLE_SIZE-1)
        return self.TABLE_SIZE-1

    def __getitem__(self, key: K) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.

        :complexity: O(n)
        Where n is the number of locations it has in the IHT's tables. 
        """
        # This is also O(n), but they just combine in comp.
        positions = self.get_location(key)
        current = self
        # Go through each position, until you can return the value
        for pos in positions:
            current = current.origin[pos][1]
        return current

    def __setitem__(self, key: K, value: V) -> None:
        """
        Set an (key, value) pair in our hash table.

        :complexity: O(n)
        Where n is the number of tables we have to traverse.
        """
        # Current table, used to traverse through tables.
        current = self
        table_position = current.hash(key)

        while current.origin[table_position] != None:
            if type(current.origin[table_position][1]) != InfiniteHashTable:
                # Ensure that what we are overriding is not lost.
                prev_key, prev_value = current.origin[table_position]
                # Increase level and add link to next table, and carry over keys and values
                next_table = InfiniteHashTable(level=current.level + 1)
                next_table[prev_key] = prev_value
                next_table[key] = value
                # We use a * to denote that it is not a full word, so that sort keys is easier to do.
                current.origin[table_position] = (key[:current.level+1] + "*", next_table)
                self.count += 1
                return
            else:
                # If it's an iht, we want to go through it until we find a place to put our key.
                current = current.origin[table_position][1]
                table_position = current.hash(key)
        current.origin[table_position] = (key, value)
        self.count += 1

    def __delitem__(self, key: K) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.

        :complexity best: O(n)
        :complexity worst: O(n^2)
        Where n is the number of tables we need to traverse to reach the key. 
        Becomes n^2 in the case we need to close down all tables except origin. 
        """
        positions = self.get_location(key)
        current_table = self
        pos_index = 0
        # Go until the final IHT
        for pos_index in range(len(positions) - 1):
            current_table = current_table.origin[positions[pos_index]][1]
        # Now current_table is the final IHT
        # Delete
        current_table.origin[positions[len(positions)-1]] = None
        # Because the count is all branching elements
        self.count -= 1
        # Now we need to check whether deleting causes IHT's to be closed down.
        isDeleting = True
        while isDeleting:
            if current_table == self:
                break
            item = None
            num_elements = 0
            for element in current_table.origin:
                if element is not None:
                    if element[0][len(element[0])-1] != "*":
                        item = element
                        num_elements += 1
            if num_elements <= 1 and item is not None:
                # We want to store this singular key, value, and insert it after we deleted the IHT.
                item_key, item_value = item
                # We need to go until the table before current table, and find current table's position in prev table and delete.
                prev_table = self
                for pos in positions[:pos_index]:
                    prev_table = prev_table.origin[pos][1]
                prev_table.origin[positions[pos_index]] = None
                # Have to decrease, because when we insert it will increase.
                self.count -= 1
                current_table = prev_table
                pos_index -= 1
                self[item_key] = item_value
            else:
                isDeleting = False
        
    def __len__(self) -> int:
        """
        Returns the number of elements inside current table, and all sub_tables.
        """
        return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        pass

    def get_location(self, key) -> list[int]:
        """
        Get the sequence of positions required to access this key.

        :raises KeyError: when the key doesn't exist.

        :complexity: O(n)
        Where n is the number of tables needed to traverse until key is found.
        """
        res = []
        current_table = self
        while type(current_table) is InfiniteHashTable:
            # Hashing is a constant operation
            table_position = current_table.hash(key)
            entry = current_table.origin[table_position]
            if entry is None:
                raise KeyError
            res.append(table_position)
            current_table = entry[1]
        entry_key, entry_value = entry
        if entry_key != key:
            raise KeyError
        return res

    def __contains__(self, key: K) -> bool:
        """
        Checks to see if the given key is in the Hash Table

        :complexity: See get item.
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True

    def sort_keys(self, current=None) -> list[str]:
        """
        Recursively returns all keys currently in the table in lexicographically sorted order.

        :current: current IHT we are looking at. Default to None, which becomes self.

        :complexity: O(TABLE_SIZE*n)
        Where n is the number of tables we iterate through to accumulate all values. 
        """
        res = []
        if current == None:
            current_table = self
        else:
            current_table = current

        # First check pos self.TABLE_SIZE - 1, this is the place for if the key is equal to the previous pointer e.g (lin and lin*)
        if current_table.origin[current_table.TABLE_SIZE - 1] is not None and "*" not in current_table.origin[current_table.TABLE_SIZE - 1][0]:
            res += [current_table.origin[current_table.TABLE_SIZE - 1][0]]
        # To sort lexicographically, start at a and finish at z.
        start_pos = ord('a') % (self.TABLE_SIZE - 1)
        table_position = start_pos
        for _ in range(current_table.TABLE_SIZE):
            entry = current_table.origin[table_position]
            # Ignore none and *last slot
            if entry is not None and table_position != current_table.TABLE_SIZE - 1:
                key, value = entry
                if "*" in key:
                    # Recursive call on next table.
                    res += self.sort_keys(value)
                else:
                    res += [key]
            # Wrap around
            table_position = (table_position + 1) % self.TABLE_SIZE
        return res
