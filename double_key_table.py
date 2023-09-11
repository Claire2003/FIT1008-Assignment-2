from __future__ import annotations

from typing import Generic, TypeVar, Iterator
from data_structures.hash_table import LinearProbeTable, FullError
from data_structures.referential_array import ArrayR

K1 = TypeVar('K1')
K2 = TypeVar('K2')
V = TypeVar('V')

class DoubleKeyTable(Generic[K1, K2, V]):
    """
    Double Hash Table.

    Type Arguments:
        - K1:   1st Key Type. In most cases should be string.
                Otherwise `hash1` should be overwritten.
        - K2:   2nd Key Type. In most cases should be string.
                Otherwise `hash2` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    # No test case should exceed 1 million entries.
    TABLE_SIZES = [5, 13, 29, 53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613, 393241, 786433, 1572869]

    HASH_BASE = 31

    def __init__(self, sizes:list|None=None, internal_sizes:list|None=None) -> None:
        self.elementCount = 0
        if sizes is None:
            self.table[self.TABLE_SIZES]
        else:
            self.table = LinearProbeTable(sizes)
        if internal_sizes is None:
            self.internal_sizes = self.TABLE_SIZES
        else:
            self.internal_sizes = internal_sizes
        

    def hash1(self, key: K1) -> int:
        """
        Hash the 1st key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % self.table_size
            a = a * self.HASH_BASE % (self.table_size - 1)
        return value

    def hash2(self, key: K2, sub_table: LinearProbeTable[K2, V]) -> int:
        """
        Hash the 2nd key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % sub_table.table_size
            a = a * self.HASH_BASE % (sub_table.table_size - 1)
        return value

    def _linear_probe(self, key1: K1, key2: K2, is_insert: bool) -> tuple[int, int]:
        """
        Find the correct position for this key in the hash table using linear probing.

        :raises KeyError: When the key pair is not in the table, but is_insert is False.
        :raises FullError: When a table is full and cannot be inserted.
        """
        # Starting implementation
        table_position = self.hash1(key1)

        for _ in range(len(self.table)):
            if self.table[table_position] is None:
                if not is_insert:
                    raise KeyError
                else:
                    # Create subtable if is_insert is true and this is the first pair with key1.
                    sub_table = LinearProbeTable(self.internal_sizes)
                    self.table[table_position] = (key1, sub_table)
                    sub_table.hash = lambda k: self.hash2(k, sub_table)
                    sub_table_position = self.hash2(key2, self.table[table_position])
                    # No need to linear probe, freshly created table. 
                    return (table_position, sub_table_position)
            elif self.table[table_position][0] == key1: 
                # Might have to change this, not sure.
                # With 1D key table, this works because no matter is_insert, you'll want to either return cause you found
                # Or insert to replace/update data at the correct position, and this place is insertable.
                # With 2D key table, Might have to check inside, see if it has a subtable, if not, return tableposition
                # If yes, go through subtable, return table position. 
                sub_table = self.table[table_position][1]
                if type(sub_table) is LinearProbeTable:
                    sub_table_position = sub_table._linear_probe(key2, is_insert)
                # for _ in range(len(sub_table)):
                #     if sub_table[sub_table_position] is None:
                #         if not is_insert:
                #             raise KeyError
                #         else:
                #             return (table_position, sub_table_position)
                #     elif sub_table[sub_table_position] == key2:
                #         return (table_position, sub_table_position)
                #     else:
                #         sub_table_position = (sub_table_position + 1) % len(sub_table)
                #     raise FullError
                return (table_position, sub_table_position)
            else:
                table_position = (table_position + 1) % len(self.table)
        raise FullError
        

    def iter_keys(self, key:K1|None=None) -> Iterator[K1|K2]:
        """
        key = None:
            Returns an iterator of all top-level keys in hash table
        key = k:
            Returns an iterator of all keys in the bottom-hash-table for k.
        """
        raise NotImplementedError()

    def keys(self, key:K1|None=None) -> list[K1|K2]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.
        """
        if key == None:
            return self.table.keys()
        else:
            return self.table[self.table._linear_probe(key, False)].keys()

    def iter_values(self, key:K1|None=None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.
        """
        raise NotImplementedError()

    def values(self, key:K1|None=None) -> list[V]:
        """
        key = None: returns all values in the table.
        key = x: returns all values for top-level key x.
        """
        if key == None:
            return self.table.values()
        else:
            return self.table[self.table._linear_probe(key, False)][1].values()

    def __contains__(self, key: tuple[K1, K2]) -> bool:
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

    def __getitem__(self, key: tuple[K1, K2]) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """
        key1 = key[0]
        key2 = key[1]

        if self.__contains__(key):
            position_tuple = self._linear_probe(key1, key2, False)
            return self.table[position_tuple[0]][position_tuple[1]][1] # VALUE
        raise KeyError("Key does not exist")


        if self.__contains__(key,[K1,K2]):
            first_hash = self.hash1(key[0])
            return self.hash2(key[1],first_hash)
        else:
            raise Exception("KeyError: the key does not exist")

    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """
        key1 = key[0]
        key2 = key[1]
        position_tuple = self._linear_probe(key1, key2, False)
        self.table[position_tuple[0]][position_tuple[1]][1] = data

    def __delitem__(self, key: tuple[K1, K2]) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        raise NotImplementedError()

    def _rehash(self) -> None:
        """
        Need to resize table and reinsert all values

        :complexity best: O(N*hash(K)) No probing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) Lots of probing.
        Where N is len(self)
        """
        raise NotImplementedError()

    def table_size(self) -> int:
        """
        Return the current size of the table (different from the length)
        """
        return self.table.table_size

    def __len__(self) -> int:
        """
        Returns number of elements in the hash table
        """
        return self.elementCount

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        raise NotImplementedError()
