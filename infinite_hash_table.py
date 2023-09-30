from __future__ import annotations
from typing import Generic, TypeVar

from data_structures.referential_array import ArrayR
from data_structures.hash_table import LinearProbeTable

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
        self.level = level
        self.count = 0
        self.origin:ArrayR[tuple[K, V]] = ArrayR(self.TABLE_SIZE)

    def hash(self, key: K) -> int:
        if self.level < len(key):
            return ord(key[self.level]) % (self.TABLE_SIZE-1)
        return self.TABLE_SIZE-1

    def __getitem__(self, key: K) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """
        positions = self.get_location(key)
        current = self
        for pos in positions:
            current = current.origin[pos][1]
        return current

    def __setitem__(self, key: K, value: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """
        # sub_table.hash = lambda k: self.hash2(k, sub_table) # Set hash function of sub table. 

        # Logic:
        # First table: Find table position
        # If theres None, we can enter it.
        # If theres something there, we should create a new hash table,
        # For example, lin and linked.
        # We have lin, but in the first table now we have key l, and value IHT
        # The following IHT, we have li and value IHT
        # We create as many IHT's as there are duplicate letters.

        # Start with one iht.
        # Given the level, if there ends up being duplicate letters, create a new hash table, and reinsert
        current = self
        # If it's an iht, we wanna go through it until we find a place to put our key.
        table_position = current.hash(key)

        while current.origin[table_position] != None: # and current.origin[table_position][0][:current.level + 1] == key[:current.level + 1]
            if type(current.origin[table_position][1]) != InfiniteHashTable:
                prev_key, prev_value = current.origin[table_position]
                next_table = InfiniteHashTable(level=current.level + 1)
                next_table[prev_key] = prev_value
                next_table[key] = value
                current.origin[table_position] = (key[:current.level+1] + "*", next_table)
                # We use a * to denote that it is not a full word, so that sort keys is easier to do.
                self.count += 1
                return
            else:
                current = current.origin[table_position][1]
                table_position = current.hash(key)
        current.origin[table_position] = (key, value)
        self.count += 1

    def __delitem__(self, key: K) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
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
        """
        # Probably can do with recursion. Base case when key in table is key.
        # Then when we go back accum. But for now try loop version
        res = []
        current_table = self
        while type(current_table) is InfiniteHashTable:
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

        :complexity: See linear probe.
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True

    def sort_keys(self, current=None) -> list[str]:
        """
        Returns all keys currently in the table in lexicographically sorted order.
        """
        res = []
        if current == None:
            current_table = self
        else:
            current_table = current

        # First check pos self.TABLE_SIZE - 1
        if current_table.origin[current_table.TABLE_SIZE - 1] is not None and "*" not in current_table.origin[current_table.TABLE_SIZE - 1][0]:
            res += [current_table.origin[current_table.TABLE_SIZE - 1][0]]

        start_pos = ord('a') % (self.TABLE_SIZE - 1)
        table_position = start_pos
        for _ in range(current_table.TABLE_SIZE):
            entry = current_table.origin[table_position]
            # Ignore none and *last slot
            if entry is not None and table_position != current_table.TABLE_SIZE - 1:
                key, value = entry
                if "*" in key:
                    res += self.sort_keys(value)
                else:
                    res += [key]
            table_position = (table_position + 1) % self.TABLE_SIZE
        return res
