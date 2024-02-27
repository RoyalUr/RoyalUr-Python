from royalur.game import Game
from royalur.lut.board_encoder import SimpleGameStateEncoding
from royalur.model.board import Piece
from royalur.rules.state.state import WinGameState
import threading
import queue


# Constants
OCCUPANTS_MASK = 0b11
LIGHT_ONLY_FLAG = 0b100
LIGHT_PATH_INDEX_SHIFT = 3
LIGHT_PATH_INDEX_MASK = 0b11111
DARK_PATH_INDEX_SHIFT = 8
DARK_PATH_INDEX_MASK = 0b11111
BOARD_WIDTH = 3
BOARD_HEIGHT = 8


def calculate_next_board_indices(tile_flags):
    width = BOARD_WIDTH
    height = BOARD_HEIGHT
    board_index_count = len(tile_flags)

    next_board_indices = [0] * board_index_count
    for index in range(board_index_count):
        next_x = index % width
        next_y = index // width
        while True:
            next_y += 1
            if next_y >= height:
                next_x += 1
                next_y = 0
            if (
                next_x >= width
                or (tile_flags[next_x + width * next_y] & OCCUPANTS_MASK) != 1
            ):
                break

        next_index = next_x + width * next_y
        if next_x >= width:
            next_index = board_index_count
        next_board_indices[index] = next_index

    return next_board_indices


def calculate_tile_flags(board_index_count):
    width = BOARD_WIDTH
    height = BOARD_HEIGHT

    light_path = [
        (1, 4),
        (1, 3),
        (1, 2),
        (1, 1),
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
        (2, 5),
        (2, 6),
        (2, 7),
        (2, 8),
        (1, 8),
        (1, 7),
    ]
    dark_path = [
        (3, 4),
        (3, 3),
        (3, 2),
        (3, 1),
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
        (2, 5),
        (2, 6),
        (2, 7),
        (2, 8),
        (3, 8),
        (3, 7),
    ]

    tile_flags = [0] * board_index_count
    for board_x in range(width):
        for board_y in range(height):
            tile = (board_x + 1, board_y + 1)
            index = board_x + width * board_y

            occupants = 1
            tile_light_only = False
            light_index = 0
            dark_index = 0
            if tile in light_path:
                occupants += 1
                tile_light_only = True
                light_index = light_path.index(tile)
            if tile in dark_path:
                occupants += 1
                tile_light_only = False
                dark_index = dark_path.index(tile)

            light_only_flag = LIGHT_ONLY_FLAG if tile_light_only else 0
            occupants_flag = occupants & OCCUPANTS_MASK
            light_path_flag = (
                light_index & LIGHT_PATH_INDEX_MASK
            ) << LIGHT_PATH_INDEX_SHIFT
            dark_path_flag = (
                dark_index & DARK_PATH_INDEX_MASK
            ) << DARK_PATH_INDEX_SHIFT
            tile_flags[index] = (
                light_only_flag | occupants_flag | light_path_flag | dark_path_flag
            )

    return tile_flags


board_index_count = BOARD_WIDTH * BOARD_HEIGHT
tile_flags = calculate_tile_flags(board_index_count)
next_board_indices = calculate_next_board_indices(tile_flags)
# Create a thread-safe queue
my_queue = queue.Queue()


def produce_states():
    """
    Loop through all possible game states and print them.
    """
    print("Producing states")
    # Create a game
    game = Game.create_finkel()
    piece_count = 7

    current_state = game.get_current_state()
    light_player = current_state._light_player
    dark_player = current_state._dark_player

    for light_pieces in range(piece_count + 1):
        for dark_pieces in range(piece_count + 1):
            board = current_state._board
            board.clear()
            light_player._piece_count = light_pieces
            light_player._score = piece_count - light_pieces
            dark_player._piece_count = dark_pieces
            dark_player._score = piece_count - dark_pieces

            loop_board_states(game, 0)
    game_consumer(None)


def consume_states():
    encoding = SimpleGameStateEncoding()
    print("Consuming states")
    consumed_count = 0
    BUFFER_SIZE = 1000000
    game_buffer = [None] * BUFFER_SIZE
    while True:
        state_data = my_queue.get()
        if state_data is None:
            final_consume(consumed_count, game_buffer, BUFFER_SIZE)
            break
        board = state_data["board"]
        light_score = state_data["light_player_score"]
        dark_score = state_data["dark_player_score"]
        board_state = "".join(
            [
                piece._owner._character if piece is not None else "."
                for piece in board._pieces
            ]
        )
        game_buffer[consumed_count % BUFFER_SIZE] = f"{board_state} {light_score} {dark_score} {encoding.encode_board(board)}\n"
        consumed_count += 1
        if consumed_count % BUFFER_SIZE == 0 and consumed_count > 0:
            with open(f"game_states_{consumed_count // BUFFER_SIZE}.txt", "w") as f:
                f.write("".join(game_buffer))
            print(f"Consumed {consumed_count} games")
            game_buffer = [None] * BUFFER_SIZE


def loop_light_game_states():
    produce_thread = threading.Thread(target=produce_states)
    consume_thread = threading.Thread(target=consume_states)

    produce_thread.start()
    consume_thread.start()

    produce_thread.join()
    consume_thread.join()


def game_consumer(game):
    if game is None:
        my_queue.put(None)
        return
    state = game._states[-1]
    my_queue.put(
        {
            "board": state._board.copy(),
            "light_player_score": state._light_player._score,
            "dark_player_score": state._dark_player._score,
        }
    )


def final_consume(consumed_count, game_buffer, BUFFER_SIZE):
    with open(f"game_states_{(consumed_count // BUFFER_SIZE) + 1}.txt", "w") as f:
        for stuff_tuple in game_buffer:
            if stuff_tuple is not None:
                board_state, light_score, dark_score, lut_encoding = stuff_tuple
                f.write(f"{board_state} {light_score} {dark_score} {lut_encoding}\n")
    print(f"Consumed {consumed_count} games")


def loop_board_states(game, board_index):
    global board_index_count, tile_flags, next_board_indices
    starting_piece_count = 7
    board_index_count = board_index_count

    tile_flag = tile_flags[board_index]
    light_only = (tile_flag & LIGHT_ONLY_FLAG) != 0
    occupants = tile_flag & OCCUPANTS_MASK
    next_board_index = next_board_indices[board_index]

    current_state = game.get_current_state()
    light_player = current_state._light_player
    dark_player = current_state._dark_player
    original_light_score = light_player.score
    original_dark_score = dark_player.score

    for occupant in range(occupants):
        new_light_score = original_light_score
        new_dark_score = original_dark_score
        new_piece = 0
        if occupant == 1:
            if light_only:
                light_index = (
                    tile_flag >> LIGHT_PATH_INDEX_SHIFT
                ) & LIGHT_PATH_INDEX_MASK
                new_piece = light_index + 1
                new_light_score -= 1
            else:
                dark_index = (tile_flag >> DARK_PATH_INDEX_SHIFT) & DARK_PATH_INDEX_MASK
                new_piece = dark_index + 1
                new_dark_score -= 1
        elif occupant == 2:
            light_index = (tile_flag >> LIGHT_PATH_INDEX_SHIFT) & LIGHT_PATH_INDEX_MASK
            new_piece = light_index + 1
            new_light_score -= 1
        if new_light_score < 0 or new_dark_score < 0:
            continue

        if new_piece != 0:
            current_state._board._pieces[board_index] = Piece(
                (
                    dark_player
                    if original_dark_score != new_dark_score
                    else light_player
                ).player,
                new_piece,
            )
        else:
            current_state._board._pieces[board_index] = None
        light_player._score = new_light_score
        dark_player._score = new_dark_score

        if next_board_index >= board_index_count:
            dark_won = new_dark_score >= starting_piece_count
            if dark_won:
                continue
            if new_light_score >= starting_piece_count:
                game.add_state(
                    WinGameState(
                        current_state._board,
                        light_player,
                        dark_player,
                        light_player.player,
                    )
                )
            game_consumer(game)
        else:
            loop_board_states(game, next_board_index)
