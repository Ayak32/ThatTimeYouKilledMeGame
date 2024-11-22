import sys
import pickle
import time

from decimal import Decimal, setcontext, BasicContext
from datetime import datetime
from board import Board
from movehistory import MoveHistory
from player import PlayerFactory, HumanPlayer, HeuristicAIPlayer, RandomAIPlayer

from enum import Enum
from typing import Optional, Dict, Callable

class GameState(Enum):
    PLAYING = "playing"
    WHITE_WON = "white_won"
    BLACK_WON = "black_won"
    DRAW = "draw"

class Game:
    """Manages the game flow and user interactions."""
    
    def __init__(self, white_type="human", black_type="human", undo_redo="off", score="off"):
        """Initialize the game with specified player types and settings."""
    
        self.board = Board()
        self.board.score = score.lower() == "on"
        
        self.w_player = PlayerFactory.create_player(white_type, "w_player", self.board)
        self.b_player = PlayerFactory.create_player(black_type, "b_player", self.board)
        
        self.board.w_player = self.w_player
        self.board.b_player = self.b_player
        self.board.current_player = self.w_player
        self.board._setupBoard()
        # Initialize game components
        
        self.current_player = self.w_player
        self.move_history = MoveHistory()
        
        # Game settings
        self.undo_redo = undo_redo.lower() == "on"
        self.score = score.lower() == "on"
        self.state = GameState.PLAYING
        self.turn_number = 1
        
    def _display_eras(self):
        """Display the current state of all eras."""
        print("---------------------------------")
        
        # Display black's focus indicator
        if self.b_player.current_era == self.board.future:
            print(" " * 26 + "black")
        elif self.b_player.current_era == self.board.present:
            print(" " * 14 + "black")
        else:
            print(" " * 2 + "black")
        
        # Display all three eras side by side
        self._display_era_rows(self.board.past, self.board.present, self.board.future)
        

        # Display white's focus indicator
        if self.w_player.current_era == self.board.future:
            print(" " * 26 + "white")
        elif self.w_player.current_era == self.board.present:
            print(" " * 14 + "white")
        else:
            print(" " * 2 + "white")
        
            
        # Display turn information
        print(f"Turn: {self.turn_number}, Current player: {'white' if self.current_player == self.w_player else 'black'}")
    
    def _display_era_rows(self, past, present, future):
        """Helper method to display rows of all eras side by side."""
        for y in range(4):
            # Display grid lines
            print("+-+-+-+-+   +-+-+-+-+   +-+-+-+-+")
            
            # Display pieces in each era
            past_row = self._format_row(past.grid[y])
            present_row = self._format_row(present.grid[y])
            future_row = self._format_row(future.grid[y])
            print(f"{past_row}   {present_row}   {future_row}")
        
        # Bottom grid line
        print("+-+-+-+-+   +-+-+-+-+   +-+-+-+-+")
    
    def _format_row(self, row):
        """Format a single row of an era for display."""
        row_str = "|"
        for space in row:
            if space.isOccupied():
                piece = space.getPiece()
                # Use the piece's ID directly instead of calculating it
                symbol = piece.id
            else:
                symbol = " "
            row_str += f"{symbol}|"
        return row_str
    
    def run(self):
        """Run the game loop"""
        while True:  # Outer loop for multiple games
            while self.state == GameState.PLAYING:
                self._display_eras()
                # print(f"Turn: {self.turn_number}, Current player: {'white' if self.current_player == self.w_player else 'black'}")
                
                # Get and execute move
                move = self.current_player.getMove(self.board)
                if move:
                    success = self.board.makeMove(move)
                    if success:
                        self.move_history.addMove(move)
                        print(move)
                        
                        # Update game state
                        self._handle_game_end()
                        self.current_player = self.b_player if self.current_player == self.w_player else self.w_player
                        self.turn_number += 1
            
            # Game has ended, ask to play again
            print("play again?")
            play_again = input().lower().strip()
            if play_again != "yes":
                break
                
            # Reset the game for a new round
            self.reset_game()  # No need to call _setupBoard separately anymore
    
    def _handle_undo_redo(self) -> str:
        """Handle undo/redo functionality."""
        while True:
            choice = input("Enter 'undo', 'redo', or 'next': ").lower()
            if choice == "undo":
                if self.move_history.undo(self.board):
                    self.turn_number -= 1
                    self.current_player = self.b_player if self.current_player == self.w_player else self.w_player
                else:
                    print("Cannot undo further")
            elif choice == "redo":
                if self.move_history.redo(self.board):
                    self.turn_number += 1
                    self.current_player = self.b_player if self.current_player == self.w_player else self.w_player
                else:
                    print("Cannot redo further")
            elif choice == "next":
                return choice
            else:
                print("Invalid choice")
    
    def _display_scores(self):
        """Display current game scores for both players."""
        w_scores = self._calculate_player_scores(self.w_player)
        b_scores = self._calculate_player_scores(self.b_player)
        
        print("\nScores:")
        print(f"White - Era Presence: {w_scores['era_presence']}, "
              f"Piece Advantage: {w_scores['piece_advantage']}, "
              f"Supply: {w_scores['supply']}, "
              f"Centrality: {w_scores['centrality']}, "
              f"Focus: {w_scores['focus']}")
        print(f"Black - Era Presence: {b_scores['era_presence']}, "
              f"Piece Advantage: {b_scores['piece_advantage']}, "
              f"Supply: {b_scores['supply']}, "
              f"Centrality: {b_scores['centrality']}, "
              f"Focus: {b_scores['focus']}")
    
    # def _calculate_player_scores(self, player) -> Dict[str, int]:
    #     """Calculate various scores for a player."""
    #     return {
    #         'era_presence': self._calculate_era_presence(player),
    #         'piece_advantage': self._calculate_piece_advantage(player),
    #         'supply': self._calculate_supply(player),
    #         'centrality': self._calculate_centrality(player),
    #         'focus': self._calculate_focus(player)
    #     }
    
    def _handle_game_end(self):
        """Check if the game has ended and update state accordingly"""
        # Check if either player has pieces in only one era
        w_eras = self._count_player_eras(self.w_player)
        b_eras = self._count_player_eras(self.b_player)
        
        if w_eras <= 1:
            self.state = GameState.BLACK_WON
            self._display_eras()
            print("black has won")
            return
            
        if b_eras <= 1:
            self.state = GameState.WHITE_WON
            self._display_eras()
            print("white has won")
            return
    
    def reset_game(self):
        """Reset the game to initial state."""
        # Store current settings
        white_type = "heuristic" if isinstance(self.w_player, HeuristicAIPlayer) else "random" if isinstance(self.w_player, RandomAIPlayer) else "human"
        black_type = "heuristic" if isinstance(self.b_player, HeuristicAIPlayer) else "random" if isinstance(self.b_player, RandomAIPlayer) else "human"
        undo_redo = "on" if self.undo_redo else "off"
        score = "on" if self.score else "off"
        
        # Reinitialize everything
        self.board = Board()
        self.board.score = score.lower() == "on"
        
        # Recreate players
        self.w_player = PlayerFactory.create_player(white_type, "w_player", self.board)
        self.b_player = PlayerFactory.create_player(black_type, "b_player", self.board)
        
        # Reset board references
        self.board.w_player = self.w_player
        self.board.b_player = self.b_player
        self.board.current_player = self.w_player
        
        # Reset game state
        self.current_player = self.w_player
        self.move_history = MoveHistory()
        self.state = GameState.PLAYING
        self.turn_number = 1
        
        # Setup the board
        self.board._setupBoard()

    # def _calculate_era_presence(self, player) -> int:
    #     """Calculate number of eras where player has pieces."""
    #     count = 0
    #     for era in [self.board.past, self.board.present, self.board.future]:
    #         if era.getPieces(player.color):
    #             count += 1
    #     return count

    # def _calculate_piece_advantage(self, player) -> int:
    #     """Calculate piece advantage over opponent."""
    #     player_pieces = sum(len(era.getPieces(player.color)) 
    #                       for era in [self.board.past, self.board.present, self.board.future])
    #     opponent_pieces = sum(len(era.getPieces(self._get_opponent(player).color)) 
    #                         for era in [self.board.past, self.board.present, self.board.future])
    #     return player_pieces - opponent_pieces

    # def _calculate_supply(self, player) -> int:
    #     """Calculate remaining supply for player."""
    #     total_pieces = sum(len(era.getPieces(player.color)) 
    #                      for era in [self.board.past, self.board.present, self.board.future])
    #     return 9 - total_pieces  # Assuming 9 total pieces per player

    # def _calculate_centrality(self, player) -> int:
    #     """Calculate how many pieces are in central positions."""
    #     central_count = 0
    #     central_positions = [(1,1), (1,2), (2,1), (2,2)]
    #     for era in [self.board.past, self.board.present, self.board.future]:
    #         for x, y in central_positions:
    #             space = era.getSpace(x, y)
    #             if space.isOccupied() and space.getPiece().owner == player.color:
    #                 central_count += 1
    #     return central_count

    # def _calculate_focus(self, player) -> int:
    #     """Calculate number of pieces in current focus era."""
    #     return len(self.board.current_era.getPieces(player.color))

    # def _get_opponent(self, player):
    #     """Get the opponent of the given player."""
    #     return self.b_player if player == self.w_player else self.w_player

    def get_winner(self) -> GameState:
        """Determine the winner of the game"""
        w_pieces = 0
        b_pieces = 0
        
        # Count pieces for each player across all eras
        for era in [self.board.past, self.board.present, self.board.future]:
            w_pieces += len(era.getPieces(self.w_player))
            b_pieces += len(era.getPieces(self.b_player))
        
        # If white has no pieces, black wins
        if w_pieces == 0:
            return GameState.BLACK_WON
        # If black has no pieces, white wins
        elif b_pieces == 0:
            return GameState.WHITE_WON
        # If both have pieces, game continues
        return GameState.PLAYING

    def _count_player_eras(self, player: 'PlayerStrategy') -> int:
        """Count number of eras containing player's pieces"""
        count = 0
        for era in [self.board.past, self.board.present, self.board.future]:
            if len(era.getPieces(player)) > 0:
                count += 1
        return count





# class Game():
#     """Display a menu and respond to choices when run."""

#     def __init__(self, white_type="human", black_type="human", undo_redo="off", score="off"):
#         self.w_player = PlayerFactory(white_type, "white")
#         self.b_player = PlayerFactory(black_type, "black")
#         # self.players = [player_w, player_b]
        
#         self.board = Board()
#         self.current_player = self.w_player
#         self.move_history = MoveHistory()
#         self.turn_number = 1

        
#         # self.white_type = white_type
#         # self.black_type = black_type
#         self.undo_redo = undo_redo
#         self.score = score


#     def display_eras(self):
#         """Display the eras"""

#         print("---------------------------------")
#         # function to print the eras
#         # turn & current player print(game.turn)

#     def run(self):
#         """Display the menu and respond to choices."""

#         while True:
#             self.display_menu()
#             choice = input(">")
#             action = self.choices.get(choice)
#             if action:
#                 action()
#             else:
#                 print("{0} is not a valid choice".format(choice))

#     def play_turn(self):
#         # Player selects a move based on current board state
#         move = self.current_player.select_move(self.board)
        
#         # Validate and execute move
#         if self.board.is_valid_move(move):
#             # Save current state before move
#             self.history.save_state(self.board)
            
#             # Execute move
#             move.execute(self.board)
            
#             # Check for game end
#             if self.check_game_end():
#                 self.declare_winner()
            
#             # Switch players
#             self.current_player = (self.white_player if self.current_player == self.black_player 
#                                    else self.black_player)
#             self.play_turn += 1
    
#     def reset_game(self):
#         return
        




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
        
        # Start the game with the parsed or default arguments
        Game(white_type=white_type, black_type=black_type, undo_redo=undo_redo, score=score).run()
    except ValueError as error:
        print(f"Error: {error}")

