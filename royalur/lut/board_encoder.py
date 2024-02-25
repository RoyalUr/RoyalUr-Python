from typing import List

from royalur.model.player import PlayerType


class SimpleGameStateEncoding:
    def __init__(self):
        self.middle_lane_compression = self.generate_middle_lane_compression()

        max_compressed = max(self.middle_lane_compression)
        bits = 1
        while max_compressed > (1 << bits):
            bits += 1
        if bits != 13:
            raise RuntimeError("Expected the middle lane to take 13 bits")

    def generate_middle_lane_compression(self) -> List[int]:
        middle_lane_compression = [-1] * 0xFFFF
        states = []
        self.add_middle_lane_states(states, 0, 7, 7, 0)

        for index, state in enumerate(states):
            middle_lane_compression[state] = index

        return middle_lane_compression

    def add_middle_lane_states(self, states, state, light_pieces, dark_pieces, index):
        next_index = index + 1
        for occupant in range(3):
            new_light_pieces = light_pieces
            new_dark_pieces = dark_pieces

            if occupant == 1:
                new_dark_pieces -= 1
                if new_dark_pieces < 0:
                    continue
            elif occupant == 2:
                new_light_pieces -= 1
                if new_light_pieces < 0:
                    continue

            new_state = state | (occupant << (2 * index))
            if next_index == 8:
                states.append(new_state)
            else:
                self.add_middle_lane_states(
                    states, new_state, new_light_pieces, new_dark_pieces, next_index
                )

    def encode_middle_lane(self, board):
        state = 0
        for index in range(8):
            piece = board._pieces[board._calc_tile_index(1, index)]
            occupant = (
                0 if piece is None else (1 if piece.owner == PlayerType.DARK else 2)
            )
            state |= occupant << (2 * index)

        compressed = self.middle_lane_compression[state]
        if compressed == -1:
            raise ValueError("Illegal board state!")

        return compressed

    def encode_side_lane(self, board, board_x):
        state = 0
        base_bit_index = 0 if board_x == 0 else 3

        for index in range(6):
            board_y = index

            if index >= 4:
                board_y += 2
                base_bit_index += 4

            piece = board._pieces[board._calc_tile_index(board_x, board_y)]
            occupant = 0 if piece is None else 1
            state |= occupant << index

        return state

    def encode_board(self, board):
        left_lane = self.encode_side_lane(board, 0)
        right_lane = self.encode_side_lane(board, 2)
        middle_lane = self.encode_middle_lane(board)
        return right_lane | (middle_lane << 6) | (left_lane << 19)

    def encode_game_state(self, game_state):
        if not game_state.get_turn() == PlayerType.LIGHT:
            raise ValueError(
                "Only game states where it is the light player's "
                "turn are supported by this encoding"
            )

        state = self.encode_board(game_state.board)
        state |= game_state.dark_player._piece_count << 25
        state |= game_state.light_player._piece_count << 28

        return state
