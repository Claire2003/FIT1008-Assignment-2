from __future__ import annotations
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

    def __init__(self,level) -> None:
        self.level = level
        self.array:ArrayR[tuple[K, V]] = ArrayR(self.TABLE_SIZE) 

    def hash(self, key: K) -> int:
        if self.level < len(key):
            return ord(key[self.level]) % (self.TABLE_SIZE-1)
        return self.TABLE_SIZE-1

    def __getitem__(self, key: K) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """
        key1, key2 = key

        if self.__contains__(key):
            table_position, sub_table_position = self._linear_probe(key1, key2, False)
            return self.table[table_position][1].array[1]
        raise KeyError(key1)

        raise NotImplementedError()

    def __setitem__(self, key: K, value: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """
        index = hash(key)
        
        # check the index
        if self.array[index] != None: 
            if type(self.array[index][1]) != list: # checking if the index has a value or an array
                store = self.array[index] # storing the value
                self.array[index] = None # erasing the value
                new_key = key[self.level]
                nextHashTable = InfiniteHashTable(self.level+1)
                self.array[index] = (new_key, nextHashTable) # adding the 
                nextHashTable.__setitem__(key, value)
                nextHashTable.__setitem__(store[0], store[1])
                """
                erase value
                make new value first letter of key
                make instance of the hashtable class
                nexthashtable = InfiniteHashTable(self.level+1)
                add key
                add erased value
                """
                
            else:
                nextHashTable = self.array[index][1]
                nextHashTable.__setitem__(key, value)
                """
                go into next hash table
                hash second letter of the key
                """
        else:
            self.array[index] = (key,value)

    def __delitem__(self, key: K) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        raise NotImplementedError()

    def __len__(self) -> int:
        raise NotImplementedError()

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        raise NotImplementedError()

    def get_location(self, key) -> list[int]:
        """
        Get the sequence of positions required to access this key.

        :raises KeyError: when the key doesn't exist.
        """
        raise NotImplementedError()

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
        raise NotImplementedError()
