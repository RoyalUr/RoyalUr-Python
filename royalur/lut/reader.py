import json
from typing import Any, Dict
import sys
import time
import numpy as np


class Lut:
    """
    This class provides a way to look up values in a look-up table (LUT).
    """

    def __init__(
        self,
        keys: bytes,
        values: bytes,
        file_metadata: Dict[str, Any],
    ):
        """
        Create a new instance of the Lut class.

        :param lut: The look-up table to use.
        """
        self._keys = keys
        self._values = values
        self._metadata = file_metadata
        self._value_size = self._metadata["value_int_size_bytes"]
        self._key_size = self._metadata["key_int_size_bytes"]
        self._map_sizes = self._metadata["size_of_maps"]
        self._len = int(len(self._keys) / self._key_size)

    def keys_as_numpy(self):
        return np.frombuffer(self._keys, dtype=f'>u{self._key_size}')

    def values_as_numpy(self):
        return np.frombuffer(self._values, dtype=f'>u{self._value_size}')

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get the metadata associated with the look-up table.

        :return: A dictionary containing the metadata.
        """
        return self._metadata

    def lookup(self, map_index: int, key: int) -> int:
        """
        Look up a value in the look-up table.

        :param key: The key to look up.
        :return: The value associated with the key.
        """
        index, _ = self._find_key_index(map_index, key)
        if index is None:
            raise KeyError(f"Key {key} not found in look-up table")
        return self._get_value_at_index(map_index, index)["value"]

    def lookup_detailed(self, map_index: int, key: int):
        """
        Look up a value in the look-up table.

        :param key: The key to look up.
        :return: The value associated with the key.
        """
        index, steps = self._find_key_index(map_index, key)
        if index is None:
            raise KeyError(f"Key {key} not found in look-up table")
        return {
            "index_of_key": index,
            "key_binary_search_steps": steps,
            "lookup_details": self._get_value_at_index(map_index, index),
        }

    def _query_bytestring(
            self,
            map_index: int,
            index_in_map: int,
            collection: bytes,
            item_size: int
    ) -> int:
        map_offset = self._get_map_offset(map_index)
        return {
            "map_offset": map_offset,
            "value": int.from_bytes(
                collection[
                    map_offset + index_in_map * item_size:
                    map_offset + (index_in_map + 1) * item_size
                ],
                byteorder="big",
                signed=False,
            ),
            "index_of_value_in_bytestring":
                map_offset + index_in_map * item_size,
            "item_size": item_size,
        }

    def _get_value_at_index(self, map_index: int, index: int) -> int:
        return self._query_bytestring(
            map_index,
            index,
            self._values,
            self._value_size,
        )

    def _get_key_at_index(self, map_index: int, index: int) -> int:
        return self._query_bytestring(
            map_index,
            index,
            self._keys,
            self._key_size,
        )

    def _get_map_offset(self, map_index):
        # compute map offset based on map index and map sizes
        return sum(self._map_sizes[:map_index]) * self._key_size

    def _find_key_index(self, map_index: int, key: int) -> tuple:
        """
        Find the index of a key in the look-up table.
        Uses binary search to find the index of the key in the keys array.
        The keys are assumed to be sorted.
        """
        low = 0
        high = self._len - 1
        steps = 0

        while low <= high:
            mid = (low + high) // 2
            mid_key = self._get_key_at_index(map_index, mid)["value"]
            if mid_key == key:
                return mid, steps
            elif mid_key < key:
                low = mid + 1
            else:
                high = mid - 1
            steps += 1
        return None, steps  # If the target is not in the array

    def __len__(self) -> int:
        return self._len

    def __str__(self) -> str:
        # lut is too large to print
        return f"Lut({self._len} entries)"

    def __repr__(self) -> str:
        return f"Lut({self._len} entries)"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Lut):
            return False
        return self._keys == other._keys \
            and self._values == other._values \
            and self._metadata == other._metadata

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self._keys, self._values))

    def __bool__(self) -> bool:
        return bool(self._keys)

    def __copy__(self) -> "Lut":
        return Lut(
            self._keys.copy(),
            self._values.copy(),
            self._metadata.copy(),
        )


class LutReader:
    """
    This class provides a way to read the look-up table (LUT) from a file.
    """

    # in bytes
    key_size = 4
    value_size = 2

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
        # then, the next header_length bytes are the json header
        # and is utf-8 encoded
        header_end = 8 + header_length
        json_header = binary_contents[8:header_end].decode("utf-8")

        # the next 4 bytes are for the number of maps
        number_of_maps = self._from_bytes(binary_contents[
            header_end:
            header_end + 4
        ])
        start_of_maps = header_end + 4
        size_of_maps = []
        for i in range(number_of_maps):
            size_of_maps.append(self._from_bytes(binary_contents[
                start_of_maps + 4 * i:
                start_of_maps + 4 * (i + 1)
            ]))
        sum_of_size_of_maps = sum(size_of_maps)

        # then, the lut keys
        lut_start = start_of_maps + 4 * number_of_maps
        lut_keys_end = lut_start + \
            LutReader.key_size * \
            sum_of_size_of_maps
        lut_keys_bytes = binary_contents[lut_start:lut_keys_end]

        # and the lut values
        lut_values_start = lut_keys_end
        lut_values_end = lut_values_start + \
            LutReader.value_size * \
            sum_of_size_of_maps
        lut_values_bytes = binary_contents[lut_values_start:lut_values_end]

        time_to_read = time.time() - start_time

        size_of_lut_in_file = sum_of_size_of_maps * (
            LutReader.key_size + LutReader.value_size
        )
        size_of_lut_bytes = sys.getsizeof(lut_keys_bytes) + \
            sys.getsizeof(lut_values_bytes)

        return Lut(
            lut_keys_bytes,
            lut_values_bytes,
            {
                "raw_header": json_header,
                "decoded_header": json.loads(json_header),
                "version": version,
                "key_int_size_bytes": LutReader.key_size,
                "value_int_size_bytes": LutReader.value_size,
                "sum_of_size_of_maps": sum_of_size_of_maps,
                "number_of_maps": number_of_maps,
                "size_of_maps": size_of_maps,
                "time_to_read_seconds": time_to_read,
                "size_of_lut_file_bytes": size_of_lut_in_file,
                "size_of_lut_python_bytes": size_of_lut_bytes,
                "size_ratio": size_of_lut_bytes / size_of_lut_in_file,
                "path": self._file_path,
                "index_of_first_key_in_file": lut_start,
                "index_of_first_value_in_file": lut_values_start,
            },
        )
