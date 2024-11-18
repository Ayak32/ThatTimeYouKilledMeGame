import sys
import pickle

from decimal import Decimal, setcontext, BasicContext
from datetime import datetime
# from board import Board
# from movehistory import MoveHistory
# from player import Player

# repl parts modeled off notebooke example from

class Game:
    """Display a menu and respond to choices when run."""

    def __init__(self, white_type="human", black_type="human", undo_redo="off", score="off"):
        self.board = Board()
        player_w = Player(white_type)
        player_b = Player(black_type)
        self.players = [player_w, player_b]
        self.current_player = None
        self.move_history = MoveHistory()
        self.white_type = white_type
        self.black_type = black_type
        self.undo_redo = undo_redo
        self.score = score


    def display_eras(self):
        """Display the eras"""

        print("---------------------------------")
        # function to print the eras
        # turn & current player print(game.turn)

    def run(self):
        """Display the menu and respond to choices."""

        while True:
            self.display_menu()
            choice = input(">")
            action = self.choices.get(choice)
            if action:
                action()
            else:
                print("{0} is not a valid choice".format(choice))

    def play_turn(self):
        return

    def reset_game(self):
        return
        




def validate_and_get_args(argv):

    if len(argv) > 5:
        raise ValueError(f"Invalid number of arguments")
    
    defaults = {
        "white_type": "human",
        "black_type": "human",
        "undo_redo": "off",
        "score": "off",
    }

    valid_player_types = {"human", "heuristic", "random"}
    valid_redo_undo_options = {"on", "off"}
    
    # Assign defaults or override with provided values
    white_type = argv[1] if len(argv) > 1 else defaults["white_type"]
    black_type = argv[2] if len(argv) > 2 else defaults["black_type"]
    undo_redo = argv[3] if len(argv) > 3 else defaults["undo_redo"]
    score = argv[4] if len(argv) > 4 else defaults["score"]
    
    # Validate inputs
    if white_type not in valid_player_types:
        raise ValueError(f"Invalid white player type '{white_type}'. Must be 'human', 'heuristic', or 'random'.")
    if black_type not in valid_player_types:
        raise ValueError(f"Invalid black player type '{black_type}'. Must be 'human', 'heuristic', or 'random'.")
    if undo_redo not in valid_redo_undo_options:
        raise ValueError(f"Invalid undo/redo option '{undo_redo}'. Must be 'on' or 'off'.")
    if score not in valid_redo_undo_options:
        raise ValueError(f"Invalid score option '{score}'. Must be 'on' or 'off'.")
    
    return white_type, black_type, undo_redo, score

if __name__ == "__main__":
    argv = sys.argv
    
    try:
        white_type, black_type, undo_redo, score = validate_and_get_args(argv)

        print(f"{white_type}, {black_type}, {undo_redo}, {score} ")
        
        # Start the game with the parsed or default arguments
        Game(white_type=white_type, black_type=black_type, undo_redo=undo_redo, score=score).run()
    except ValueError as error:
        print(f"Error: {error}")



    # OLD CODE
    # args = len(sys.argv)
    # argv = sys.argv

    # if args > 1:
    #     for x in range(args):
    #         if x <= 2 and x > 1:
    #             if argv[x] not in ["human", "heuristic", "random"]:
    #                 # error
    #                 raise ValueError(f"{argv[x]} is not a valid player type. Please indicate 'human', 'heuristic', or 'random'")
    #         elif 2 < x and x <= 4:
    #             if argv[x] not in ["on", "off"]:
    #                 # error
    #                 raise ValueError(f"{argv[x]} is not a valid input. Please indicate 'on' or 'off'")
    #         else:
    #             # error
    #             raise ValueError(f"Please include no more than 4 arguments")

    
    # Game(white_type=argv[1], black_type=argv[2], undo_redo=argv[3], score=argv[4]).run()