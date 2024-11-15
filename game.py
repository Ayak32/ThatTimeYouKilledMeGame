import sys
import pickle

from decimal import Decimal, setcontext, BasicContext
from datetime import datetime
from board import Board
from movehistory import MoveHistory
from player import Player

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

    def reset_game(self);
        


if __name__ == "__main__":
    args = sys.argc
    argv = sys.argv

    for x in range(args):
        if x <= 2 and x > 1:
            if argv[x] not in ["human", "heuristic", "random"]:
                # error
        elif 2 < x and x <= 4:
            if argv[x] not in ["on", "off"]:
                # error
        else:
            # error

    Game(white_type=argv[1], black_type=argv[2], undo_redo=argv[3], score=argv[4]).run()