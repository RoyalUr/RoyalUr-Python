import copy
import json
from typing import Any, Callable, Dict, Iterator, Tuple
import sys
import numpy as np
import time

class Lut:
    """
    This class provides a way to look up values in a look-up table (LUT).
    """

    def __init__(self, keys: np.array, values: np.array, file_metadata: Dict[str, Any]):
        """
        Create a new instance of the Lut class.

        :param lut: The look-up table to use.
        """
        self._keys = keys
        self._values = values
        self._metadata = file_metadata

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get the metadata associated with the look-up table.

        :return: A dictionary containing the metadata.
        """
        return self._metadata

    def lookup(self, key: int) -> int:
        """
        Look up a value in the look-up table.

        :param key: The key to look up.
        :return: The value associated with the key.
        """
        index = np.searchsorted(self._keys, key)
        if index >= len(self._keys) or self._keys[index] != key:
            raise KeyError(f"Key {key} not found")
        return self._values[index]

    def __getitem__(self, key: int) -> int:
        return self.lookup(key)

    def __contains__(self, key: int) -> bool:
        return key in self._keys

    def __len__(self) -> int:
        return len(self._keys)

    def __iter__(self) -> Iterator[int]:
        return iter(self._keys)

    def __str__(self) -> str:
        # lut is too large to print
        return f"Lut({len(self._keys)} entries)"

    def __repr__(self) -> str:
        return f"Lut({len(self._keys)} entries)"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Lut):
            return False
        return self._keys == other._keys and self._values == other._values

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self._keys, self._values))

    def __bool__(self) -> bool:
        return bool(self._keys)

    def __copy__(self) -> "Lut":
        return Lut(self._keys.copy(), self._values.copy(), self._metadata)

    def __deepcopy__(self, memo: Dict[int, object]) -> "Lut":
        return Lut(copy.deepcopy(self._keys, memo), copy.deepcopy(self._values, memo), copy.deepcopy(self._metadata, memo))

    def __getstate__(self) -> Dict[str, Any]:
        return {"lut": (self._keys, self._values, self._metadata)}

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self._keys, self._values, self._metadata = state["lut"]

    def __reduce__(self) -> Tuple[Callable, Tuple, Dict[str, Any]]:
        return (Lut, (self._keys, self._values, self._metadata), {})

    def __reduce_ex__(self, protocol: int) -> Tuple[Callable, Tuple, Dict[str, Any]]:
        return self.__reduce__()
    
class LutReader:
    """
    This class provides a way to read the look-up table (LUT) from a file.
    """

    # The number of bytes used to represent each key and value type.
    key_value_types = {
        0: 8,
        1: 4,
        2: 2,
        3: 1,
    }

    def __init__(self, file_path: str):
        """
        Create a new instance of the LutReader class.

        :param file_path: The path to the file containing the look-up table.
        """
        self._file_path = file_path

    def _from_bytes(self, value: bytes) -> int:
        return int.from_bytes(value, byteorder="big", signed=True)

    def read(self) -> Lut:
        """
        Read the look-up table from the file.

        :return: A dictionary containing the look-up table.
        """
        start_time = time.time()
        with open(self._file_path, "rb") as file:
            binary_contents = file.read()

        # first 3 bytes are magic number
        magic_number = binary_contents[:3]
        if magic_number != b"RGU":
            raise ValueError("Invalid magic number")
        # then, the next byte is the version number
        version = binary_contents[3]
        if version != 0:
            raise ValueError("Only version 0 is implemented")
        # then, the next 4 bytes are the number of entries in the json header
        header_length = self._from_bytes(binary_contents[4:8])
        # then, the next header_length bytes are the json header and is utf-8 encoded
        header_end = 8 + header_length
        json_header = binary_contents[8:header_end].decode("utf-8")
        # then, the next 4 bytes are key value types
        key_value_types = self._from_bytes(binary_contents[header_end:header_end + 4])
        # then, the next 4 bytes are value types
        value_types = self._from_bytes(binary_contents[header_end + 4:header_end + 8])
        # then, the next 4 bytes are the number of entries in the lut
        lut_length = self._from_bytes(binary_contents[header_end + 8:header_end + 12])

        # then, the next lut_length * key_value_types bytes are the lut keys
        key_value_size = LutReader.key_value_types[key_value_types]
        lut_start = header_end + 12
        lut_end = lut_start + lut_length * key_value_size
        lut_keys = np.frombuffer(binary_contents, dtype=f'>i{key_value_size}', count=lut_length, offset=lut_start)

        # then, the next lut_length * value_types bytes are the lut values
        value_size = LutReader.key_value_types[value_types]
        lut_values = np.frombuffer(binary_contents, dtype=f'>i{value_size}', count=lut_length, offset=lut_end)

        # explanation of the dtype argument is > for big-endian, i for integer, and the number of bytes

        # making sure the lengths of the keys and values are the same and that they are the same as the lut length in the header
        assert len(lut_keys) == len(lut_values)
        assert len(lut_keys) == lut_length

        time_to_read = time.time() - start_time

        size_of_lut_in_file = lut_length * (key_value_size + value_size)
        size_of_lut_numpy = sys.getsizeof(lut_keys) + sys.getsizeof(lut_values)

        return Lut(lut_keys, lut_values, {
            "raw_header": json_header,
            "decoded_header": json.loads(json_header),
            "version": version,
            "key_types": key_value_types,
            "key_int_size_bytes": key_value_size,
            "value_types": value_types,
            "value_int_size_bytes": value_size,
            "lut_length": lut_length,
            "time_to_read_seconds": time_to_read,
            "size_of_lut_in_file_bytes": size_of_lut_in_file,
            "size_of_lut_numpy_bytes": size_of_lut_numpy,
            "size_ratio": size_of_lut_numpy / size_of_lut_in_file,
            "path": self._file_path,
        })