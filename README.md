<p align="center">
  <img alt="RoyalUr-Python Logo" width="485" src="https://raw.githubusercontent.com/RoyalUr/RoyalUr-Python/master/docs/res/banner.png" />
</p>

This library provides a Python API for the play and analysis of games of **The Royal Game of Ur**!

### What is The Royal Game of Ur?

The Royal Game of Ur is one of the longest-living games in history, with evidence
of it being enjoyed by people who lived over 5,000 years ago!
This library aims to bring this ancient board game into the modern age by supporting
digital versions of the game, statistical analysis of its rules, and the use
of AI to play the game. A board used to play The Royal Game of Ur is shown below,
which was excavated by Sir Leonard Woolley in the 1930s.
It is currently on display at the British Museum!

<p align="center">
  <img alt="British Museum game board excavated by Sir Leonard Woolley" width="610" src="https://raw.githubusercontent.com/RoyalUr/RoyalUr-Python/master/docs/res/bm_board.png" />
</p>
<p align="center">
  Photo of an excavated board of the Royal Game of Ur that is dated to 2500 BC.<br/>
  © The Trustees of the British Museum.
</p>

### Resources

* [Read the documentation.](https://royalur.github.io/RoyalUrPython/)

* Prefer Java to Python? [Check out RoyalUr-Java.](https://github.com/RoyalUr/RoyalUr-Java)

* [Play The Royal Game of Ur on RoyalUr.net.](https://royalur.net/)

* If you want to delve deeper, join us to discuss the game by [joining our Discord!](https://discord.gg/HBP83J4qHV)


# 🔧 Installation
The RoyalUr-Python package is available to be installed through pip:
```bash
pip install royalur
```


# 🚀 Example

The following is a small example that shows the basics of creating
a game, autonomously playing through it by making random moves,
and reporting what happens in the game as it progresses.

```python
from royalur import Game
import random

# Create a new game using the Finkel rules.
game = Game.create_finkel()

while not game.is_finished():
    turn_player_name = game.get_turn().text_name

    if game.is_waiting_for_roll():
        # Roll the dice!
        roll = game.roll_dice()
        print(f"{turn_player_name}: Roll {roll.value}")

    else:
        # Make a random move.
        moves = game.find_available_moves()
        move = moves[random.randint(0, len(moves) - 1)]
        game.make_move(move)
        print(f"{turn_player_name}: {move.describe()}")

# Report the winner!
print(f"{game.get_winner().text_name} won the game!")
```

Here is a snippet from the end of the output from running
the example above:
```
Dark: Score a piece from C7
Light: Roll 2
Light: Score a piece from A8
Dark: Roll 1
Dark: Move C4 to C3
Light: Roll 1
Light: Score a piece from A7

Light won the game!
```


# 📜 Supported Rulesets

This library supports a wide range of rulesets for the
Royal Game of Ur. You may use standard sets of rules that
are commonly played, or create your own custom rulesets.

**Provided Rulesets:**
- Rules proposed by Irving Finkel (simple version).
- Rules proposed by James Masters.
- Rules for Aseb (using a different game board).

# ⚙️ Custom Rulesets

The rulesets are created by selecting several component pieces
that make up the ruleset. This includes selecting the board
shape, the path that pieces take around the board, the
dice that are used, alongside other features such as whether
rosette tiles are safe from capture. The provided values of
these components are given below, but new values can also be
created and used instead (e.g., for a new path around the board).

**Board Shapes:**
- Standard Royal Game of Ur.
- Aseb.

<p align="center">
  <img alt="Supported Board Shapes" width="241" src="https://raw.githubusercontent.com/RoyalUr/RoyalUr-Python/master/docs/res/board_shapes.png" />
</p>

**Paths:**
- Bell's path.
- Masters' path.
- Murray's path.
- Skiriuk's path.
- Aseb path proposed by Murray.

<p align="center">
  <img alt="Supported Paths" width="500" src="https://raw.githubusercontent.com/RoyalUr/RoyalUr-Python/master/docs/res/paths.png" />
</p>

**Dice:**
- Four binary die.
- Three binary die where a roll of zero is treated as a four.
- N binary die.
- N binary die where a roll of zero is treated as a roll of N+1.

**Features:**
- Number of starting pieces for each player.
- Whether rosettes are safe tiles.
- Whether landing on a rosette grants an extra roll.
- Whether capturing a piece grants an extra roll.


# 📝 License
This library is licensed under the MIT license.
[Read the license here.](LICENSE)
