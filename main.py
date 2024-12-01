from position import Position

import sys
import pickle
import time
import copy

from decimal import Decimal, setcontext, BasicContext
from datetime import datetime
from board import Board
from player import PlayerFactory, HumanPlayer, HeuristicAIPlayer, RandomAIPlayer
from movehistory import Originator, Caretaker, Memento

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
        
        # Game settings (initialize these first)
        self.undo_redo = undo_redo.lower() == "on"
        self.score = score.lower() == "on"
        self.state = GameState.PLAYING
        self.turn_number = 1
        
        # Board initialization
        self.board = Board()
        self.board.score = self.score
        
        # Player initialization
        self.w_player = PlayerFactory.create_player(white_type, "w_player", self.board)
        self.b_player = PlayerFactory.create_player(black_type, "b_player", self.board)
        
        # Set board references
        self.board.w_player = self.w_player
        self.board.b_player = self.b_player
        self.board.current_player = self.w_player
        self.board._setupBoard()
        
        # Initialize current player
        self.current_player = self.w_player
        
        # Initialize undo/redo functionality
        if self.undo_redo:
            self.originator = Originator(self)
            self.caretaker = Caretaker(self.originator)
            self.caretaker.save()
        
        # Add a flag to control board display
        self.should_display_board = True
    
    def _display_eras(self):
        """Display the current state of all eras."""
        print("---------------------------------")
        
        # Display black's focus indicator
        if self.b_player.current_era == self.board.future:
            print(" " * 26 + "black" + " " * 2)
        elif self.b_player.current_era == self.board.present:
            print(" " * 14 + "black" + " " * 2)
        else:
            print(" " * 2 + "black" + " " * 2)
        
        # Display all three eras side by side
        self._display_era_rows(self.board.past, self.board.present, self.board.future)
        

        # Display white's focus indicator
        if self.w_player.current_era == self.board.future:
            print(" " * 26 + "white" + " " * 2)
        elif self.w_player.current_era == self.board.present:
            print(" " * 14 + "white" + " " * 2)
        else:
            print(" " * 2 + "white" + " " * 2)
        
            
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
    
    def undo_redo_decorator(func):
        """Decorator to handle undo/redo functionality"""
        def wrapper(self, *args, **kwargs):
            while True:
                while self.state == GameState.PLAYING:
                    if self.should_display_board:
                        self._display_eras()
                        if self.score:
                            self._display_scores(self.w_player, "white")
                            self._display_scores(self.b_player, "black")
                    
                    if hasattr(self, 'originator'):
                        action = input("undo, redo, or next\n").strip().lower()
                        
                        if action == "undo":
                            result = self.caretaker.undo()
                            if result is None:
                                print("Cannot undo at first turn")
                                continue
                            
                            # Store the era references from the result
                            w_era = result.w_player.current_era
                            b_era = result.b_player.current_era
                            
                            # Update game state with the restored state
                            self.board = copy.deepcopy(result.board)
                            self.turn_number = result.turn_number
                            self.state = result.state
                            
                            # Restore player states including supply and piece tracking
                            # White player restoration
                            self.w_player._supply = copy.deepcopy(result.w_player._supply)
                            self.w_player._pieces = copy.deepcopy(result.w_player._pieces)
                            self.w_player._activated_pieces = copy.deepcopy(result.w_player._activated_pieces)
                            self.w_player.current_era = self.board.past if w_era == result.board.past else \
                                                    self.board.present if w_era == result.board.present else \
                                                    self.board.future
                            
                            # Black player restoration
                            self.b_player._supply = copy.deepcopy(result.b_player._supply)
                            self.b_player._pieces = copy.deepcopy(result.b_player._pieces)
                            self.b_player._activated_pieces = copy.deepcopy(result.b_player._activated_pieces)
                            self.b_player.current_era = self.board.past if b_era == result.board.past else \
                                                    self.board.present if b_era == result.board.present else \
                                                    self.board.future
                            
                            # Update current player reference
                            self.current_player = self.w_player if result.current_player._color == "w_player" else self.b_player
                            self.board.current_player = self.current_player
                            
                            # Fix piece positions on the board
                            for era in [self.board.past, self.board.present, self.board.future]:
                                for y in range(4):
                                    for x in range(4):
                                        if era.grid[y][x].isOccupied():
                                            piece = era.grid[y][x].getPiece()
                                            piece.position = Position(x, y, era)
                            self.should_display_board = True
                            continue
                        elif action == "redo":
                            result = self.caretaker.redo()
                            if result is None:
                                print("Cannot redo at latest turn")
                                continue
                            
                            # Store the era references from the result
                            w_era = result.w_player.current_era
                            b_era = result.b_player.current_era
                            
                            # Update game state with the restored state
                            self.board = copy.deepcopy(result.board)
                            self.turn_number = result.turn_number
                            self.state = result.state
                            
                            # Restore player states including supply and piece tracking
                            # White player restoration
                            self.w_player._supply = copy.deepcopy(result.w_player._supply)
                            self.w_player._pieces = copy.deepcopy(result.w_player._pieces)
                            self.w_player._activated_pieces = copy.deepcopy(result.w_player._activated_pieces)
                            self.w_player.current_era = self.board.past if w_era == result.board.past else \
                                                    self.board.present if w_era == result.board.present else \
                                                    self.board.future
                            
                            # Black player restoration
                            self.b_player._supply = copy.deepcopy(result.b_player._supply)
                            self.b_player._pieces = copy.deepcopy(result.b_player._pieces)
                            self.b_player._activated_pieces = copy.deepcopy(result.b_player._activated_pieces)
                            self.b_player.current_era = self.board.past if b_era == result.board.past else \
                                                    self.board.present if b_era == result.board.present else \
                                                    self.board.future
                            
                            # Update current player reference
                            self.current_player = self.w_player if result.current_player._color == "w_player" else self.b_player
                            self.board.current_player = self.current_player
                            
                            self.should_display_board = True
                            # Fix piece positions on the board
                            for era in [self.board.past, self.board.present, self.board.future]:
                                for y in range(4):
                                    for x in range(4):
                                        if era.grid[y][x].isOccupied():
                                            piece = era.grid[y][x].getPiece()
                                            piece.position = Position(x, y, era)
                            continue
                        elif action == "next":
                            self.should_display_board = False
                        else:
                            print("Not a valid action")
                            self.should_display_board = True
                            continue
                    
                    
                    # Get and execute move
                    move = self.current_player.getMove(self.board)
                    if move and self.board.makeMove(move):
                        print(move)
                        self.current_player = self.b_player if self.current_player == self.w_player else self.w_player
                        self.turn_number += 1
                        
                        self.state = self.get_winner()
                        
                        # Save state after successful move
                        if hasattr(self, 'originator'):
                            self.caretaker.save()
                    
                    # Reset display flag for next iteration
                    self.should_display_board = True
                print("play again?")
                play_again = input().lower().strip()
                if play_again != "yes":
                    break
                    
                # Reset the game for a new round
                self.reset_game()
        return wrapper
    
    @undo_redo_decorator
    def run(self):
        """Main game loop"""
        while True:  # Outer loop for multiple games
            while self.state == GameState.PLAYING:
                if self.should_display_board:
                    self._display_eras()
                    if self.score:
                        self._display_scores(self.w_player, "white")
                        self._display_scores(self.b_player, "black")
                
                
                # if game_state != GameState.PLAYING:
                #     print(f"Game Over! {game_state.value}")
                #     # Always prompt for play again, regardless of player types
                #     play_again = input("play again? (yes/no): ").strip().lower()
                #     if play_again == "yes":
                #         self.reset_game()
                #         continue  # Start new game
                #     else:
                #         break  # End program
                
                # Get and execute move
                move = self.current_player.getMove(self.board)
                if move and self.board.makeMove(move):
                    print(move)
                    self.current_player = self.b_player if self.current_player == self.w_player else self.w_player
                    self.turn_number += 1
                    game_state = self.get_winner()
                    # Save state after successful move
                    if hasattr(self, 'originator'):
                        self.caretaker.save()
                
                # Reset display flag for next iteration
                self.should_display_board = True
            

            print("play again?")
            play_again = input().lower().strip()
            if play_again != "yes":
                break
                
            # Reset the game for a new round
            self.reset_game()

    
    def reset_game(self):
        """Reset the game to initial state"""
        # Store current settings before reset
        white_type = "heuristic" if isinstance(self.w_player, HeuristicAIPlayer) else \
                     "random" if isinstance(self.w_player, RandomAIPlayer) else "human"
        black_type = "heuristic" if isinstance(self.b_player, HeuristicAIPlayer) else \
                     "random" if isinstance(self.b_player, RandomAIPlayer) else "human"
        
        # Reset turn counter and state
        self.turn_number = 1
        self.state = GameState.PLAYING
        
        # Reset board
        self.board = Board()
        self.board.score = self.score  # Preserve score display setting
        
        # Recreate players with same types as before
        self.w_player = PlayerFactory.create_player(white_type, "w_player", self.board)
        self.b_player = PlayerFactory.create_player(black_type, "b_player", self.board)
        
        # Reset board references
        self.board.w_player = self.w_player
        self.board.b_player = self.b_player
        self.board.current_player = self.w_player
        
        # Setup initial board state
        self.board._setupBoard()
        
        # Reset to white's turn
        self.current_player = self.w_player
        
        # Reset display flag
        self.should_display_board = True
        
        # Reset undo/redo if enabled
        if self.undo_redo:
            self.originator = Originator(self)
            self.caretaker = Caretaker(self.originator)
            self.caretaker.save()
    
    def get_winner(self) -> GameState:
        """Determine the winner of the game"""
        w_pieces = 0
        b_pieces = 0
        
        # Count pieces for each player across all eras
        for era in [self.board.past, self.board.present, self.board.future]:
            w_pieces += len(era.getPieces(self.w_player))
            b_pieces += len(era.getPieces(self.b_player))
        
        # If white has no pieces, black wins
        if w_pieces <= 1:
            print("black has won")
            return GameState.BLACK_WON
        # If black has no pieces, white wins
        elif b_pieces <= 1:
            print("white has won")
            return GameState.WHITE_WON
        # If both have pieces, game continues
        return GameState.PLAYING

    def _count_player_eras(self, player: 'PlayerStrategy') -> int:
        """Count number of eras containing player's pieces"""
        count = 0
        for era in [self.board.past, self.board.present, self.board.future]:
            # Only count pieces that belong to this player
            player_pieces = [p for p in era.getPieces(player) 
                            if p.owner == player._color 
                            and p not in player._deactivated_pieces]
            if len(player_pieces) > 0:
                count += 1
        return count

    def _display_scores(self, player, color: str):
        """Display scores for a player"""
        # Count number of eras with pieces
        eras = self._count_player_eras(player)
        
        # Count active pieces
        pieces = len(player._pieces)
        
        # Determine valid supply piece IDs based on player color
        valid_ids = ("4","5","6","7") if player._color == "b_player" else ("D","E","F","G")
        
        # Calculate available supply pieces (not activated or deactivated)
        available_supply = [p for p in player._supply
                           if p.id in valid_ids 
                           and p not in player._activated_pieces
                           and p not in player._deactivated_pieces]
        supply = len(available_supply)
        
        # Count pieces in focused era (current era)
        pieces_in_focus = len([p for p in player.current_era.getPieces(player)
                              if p.owner == player._color])  # Verify ownership
        
        # Calculate advantage using HeuristicAIPlayer's evaluation
        advantage = HeuristicAIPlayer._evaluate_piece_advantage(self.board, player)
        
        # Calculate centrality
        centrality = HeuristicAIPlayer._evaluate_centrality(self.board, player)
        
        # Display the scores
        print(f"{color}'s score: {eras} eras, {advantage} advantage, {supply} supply, "
              f"{centrality} centrality, {pieces_in_focus} in focus")



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


