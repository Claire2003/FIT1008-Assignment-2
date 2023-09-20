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
        # Element count is the number of elements in the top table only.
        self.elementCount = 0
        double_key_table.py-implementation
        if sizes is not None:
            self.TABLE_SIZES = sizes
        self.size_index = 0
        # Table is a referential array implementation
        self.table:ArrayR[tuple[K1, V]] = ArrayR(self.TABLE_SIZES[self.size_index])
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
        table_position = self.hash1(key1)

        for _ in range(self.table_size):
            if self.table[table_position] is None:
                if not is_insert:
                    # This key error occurs because we are searching for an item, and while we expect to find a cluster of items
                    # until we find our item, we end up finding a None object, which does not follow the rules.
                    raise KeyError(key1)
                else:
                    # Create subtable if is_insert is true and this is the first pair with key1.
                    sub_table = LinearProbeTable(self.internal_sizes)
                    sub_table.hash = lambda k: self.hash2(k, sub_table) # Set hash function of sub table. 
                    self.table[table_position] = (key1, sub_table)
                    # No need to linear probe, freshly created table. Position is thus hash value.
                    sub_table_position = sub_table.hash(key2)
                    return (table_position, sub_table_position)
            elif self.table[table_position][0] == key1: 
                # This means that there should already be a linear probe table created. 
                sub_table = self.table[table_position][1]
                if type(sub_table) is LinearProbeTable: # This is done throughout the program to make functions light up. Not really needed.
                    # Find the position of sub table using linear probe method
                    sub_table_position = sub_table._linear_probe(key2, is_insert)
                return (table_position, sub_table_position)
            else:
                table_position = (table_position + 1) % self.table_size # Increment and wrap around
        # We either iterate through all positions, and cant find a place to insert because it's full, 
        # Or we can't find the item.       
        if is_insert:
            raise FullError("Table is full!")
        else:
            raise KeyError(key1)
        

    def iter_keys(self, key:K1|None=None) -> Iterator[K1|K2]:
        """
        key = None:
            Returns an iterator of all top-level keys in hash table
        key = k:
            Returns an iterator of all keys in the bottom-hash-table for k.
        """
        keys = self.keys(key)
        original_keys = keys
        keys_index = 0
        # Does a generator count as an iterator? 
        # How I handled the base exception may be incorrect implementation
        # i.e An iterator uses the next() function, Perhaps when calling next(), and it not existing when it should naturally raises a BaseException
        # Not sure, come back.
        while keys_index < len(keys):
            if original_keys == self.keys():
                yield keys[keys_index] # Generators automatically raise StopIteration error
                keys_index += 1
            else:
                raise BaseException

    def keys(self, key:K1|None=None) -> list[K1|K2]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.
        """
        double_key_table.py-implementation
        if key == None:
            res = []
            for x in range(self.table_size):
                if self.table[x] is not None:
                    res.append(self.table[x][0])
            return res
        else:
            table_position = self.hash1(key)
            for _ in range(self.table_size):
                if self.table[table_position] is None:
                    raise KeyError
                elif self.table[table_position][0] == key:
                    break
                else:
                    table_position = (table_position + 1) % self.table_size
            return self.table[table_position][1].keys()
            # return self.table[self.table._linear_probe(key, False)].keys()

    def iter_values(self, key:K1|None=None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.
        """
        values = self.values(key)
        original_values = values
        values_index = 0
        while values_index < len(values):
            if original_values == self.values(key):
                yield values[values_index] # Generators automatically raise StopNextIteration error
                values_index += 1
            else:
                raise BaseException

    def values(self, key:K1|None=None) -> list[V]:
        """
        key = None: returns all values in the table.
        key = x: returns all values for top-level key x.
        """
        if key is None:
            res = []
            for x in range(self.table_size):
                if self.table[x] is not None:
                    sub_table_values = self.table[x][1].values()
                    for data in sub_table_values:
                        res.append(data)
            return res
        else:
            table_position = self.hash1(key)
            for _ in range(self.table_size):
                if self.table[table_position] is None:
                    raise KeyError
                elif self.table[table_position][0] == key:
                    break
                else:
                    table_position = (table_position + 1) % self.table_size
            return self.table[table_position][1].values()

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
        double_key_table.py-implementation
        key1, key2 = key

        if self.__contains__(key):
            table_position, sub_table_position = self._linear_probe(key1, key2, False)
            return self.table[table_position][1].array[1]
        raise KeyError(key1)

    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """
        key1, key2 = key
        table_position, sub_table_position = self._linear_probe(key1, key2, True)
        sub_table = self.table[table_position][1]
        if type(sub_table) is LinearProbeTable:
            # If it's empty that means we are adding to elementCount and the subtable count. 
            # Because elementCount is the number of elements in the top table, maybe we can use that instead of tablesize for some loops. 
            if sub_table.is_empty():
                sub_table.array[sub_table_position] = (key2, data)
                sub_table.count += 1
                self.elementCount += 1
            # Inserting into subtable if key1 already exists.
            elif sub_table.array[sub_table_position] is None:
                sub_table.array[sub_table_position] = (key2, data)
                sub_table.count += 1
            # Updating data if both keys exist.
            elif sub_table.array[sub_table_position][0] == key2:
                sub_table.array[sub_table_position] = (key2, data)
        if len(self) > self.table_size / 2:
            self._rehash()
        # Sub tables won't rehash themselves because we're not using set_item of linearprobetable
        if len(sub_table) > sub_table.table_size / 2:
            sub_table._rehash()

    def __delitem__(self, key: tuple[K1, K2]) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        key1, key2 = key
        table_position, sub_table_position = self._linear_probe(key1, key2, False)
        sub_table = self.table[table_position][1]
        if type(sub_table) is LinearProbeTable:
            # Remove the element
            sub_table.array[sub_table_position] = None
            sub_table.count -= 1
            # If the linear probe table is empty, we can remove it from the top table.
            if sub_table.is_empty():
                self.table[table_position] = None
                self.elementCount -= 1
        # Start moving over the cluster
        sub_table_position = (sub_table_position + 1) % sub_table.table_size
        # Accessing internal array is faster
        while sub_table.array[sub_table_position] is not None:
            key2, value = sub_table.array[sub_table_position]
            sub_table.array[sub_table_position] = None
            # Reinsert.
            newpos = sub_table._linear_probe(key2, True)
            sub_table.array[newpos] = (key2, value)
            sub_table_position = (sub_table_position + 1) % sub_table.table_size

    def _rehash(self) -> None:
        """
        Need to resize table and reinsert all values

        :complexity best: O(N*hash(K)) No probing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) Lots of probing.
        Where N is len(self)
        """
        old_table = self.table
        self.size_index += 1
        if self.size_index >= len(self.TABLE_SIZES):
            return
            #Cannot be resized further
        self.table:ArrayR[tuple[K1, V]] = ArrayR(self.TABLE_SIZES[self.size_index])
        self.elementCount = 0
        for item in old_table:
            if item is not None:
                key1, value = item
                if type(value) is LinearProbeTable:
                    for itm in value.array:
                        if itm is not None:
                            key2, data = itm
                            # Use self set item method to add things correctly.
                            self[(key1, key2)] = data

    @property
    def table_size(self) -> int:
        """
        Return the current size of the table (different from the length)
        """
        return len(self.table)

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
        # Scuffed string representation. 
        result = ""
        table_position = 0
        for _ in range(self.table_size):
            entry = self.table[table_position]
            if entry is not None:
                key1, value = entry
                result += "top table pos: " + str(table_position) + "(" + str(key1) + "," + str(value) + ")"
            table_position = (table_position + 1) % self.table_size
        return result
