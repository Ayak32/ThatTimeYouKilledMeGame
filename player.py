from abc import ABC, abstractmethod
from board import Board
from movehistory import Move
from board import Position
from board import Piece
import random

class PlayerFactory:
    """
    Factory for creating player strategies
    Supports different player types for each color
    """
    @staticmethod
    def create_player(player_type, color):
        """
        Create a player strategy based on type and color
        
        Args:
            player_type (PlayerType): Type of player to create
            color (str): Color of the player (white/black)
        
        Returns:
            PlayerStrategy: Instantiated player strategy
        """
        player_map = {
            "human": HumanPlayer,
            "random": RandomAIPlayer,
            "heuristic": HeuristicAIPlayer
        }
        
        # Retrieve player class, defaulting to HumanPlayer
        player_class = player_map.get(player_type, HumanPlayer)
        
        # Create and return player instance
        return player_class(color)
    



""" Strategy Pattern """

class PlayerStrategy(ABC):
    def __init__(self, color) -> None:
        self._color = color
        if color == "b_player":
            self._pieces = [
            Piece("1", color, None),
            Piece("2", color, None),
            Piece("3", color, None)
            ]

            self._supply = [
            Piece("4", color, None),
            Piece("5", color, None),
            Piece("6", color, None),
            Piece("7", color, None)]
        else:
            self._pieces = [
            Piece("A", color, None),
            Piece("B", color, None),
            Piece("C", color, None)]

            self._supply = [Piece("D", color, None),
            Piece("E", color, None),
            Piece("F", color, None),
            Piece("G", color, None)]
 

    def activate_piece(self, piece_id: str):
        """Move a piece from supply to active pieces"""
        if piece_id in self._supply:
            self._supply.remove(piece_id)
            piece = Piece(piece_id, self._color, None)
            self._pieces.append(piece)
            return piece
        return None

    def deactivate_piece(self, piece: Piece):
        """Move a piece from active to supply"""
        if piece in self._pieces:
            self._pieces.remove(piece)
            self._supply.append(piece.name)
    
    @abstractmethod
    def getMove(self, board: Board) -> Move:
        pass

class HeuristicAIPlayer(PlayerStrategy):
    pass
    # def getMove(self, board: Board) -> Move:
    #     valid_moves = board.getValidMoves(self)
    #     best_move = None
    #     best_score = float('-inf')
    #     for move in valid_moves:
    #         score = self._calculateScore(move, board)
    #         if score > best_score:
    #             best_score = score
    #             best_move = move
    #     return best_move
    
    # def calculateScore(self, move, board):
    #            """
    #     Calculate a score for a potential move
    #     Uses weighted criteria:
    #     1. Era presence
    #     2. Piece advantage
    #     3. Supply of pieces
    #     4. Centrality of pieces
    #     5. Focus on current era
    #     """
    #     # Winning move check
    #     if self._is_winning_move(move, board):
    #         return 9999  # Extremely high score
        
    #     # Individual scoring criteria
    #     era_presence = self._evaluate_era_presence(board)
    #     piece_advantage = self._evaluate_piece_advantage(board)
    #     piece_supply = self._evaluate_piece_supply(board)
    #     piece_centrality = self._evaluate_piece_centrality(move)
    #     era_focus = self._evaluate_era_focus(move, board)
        
    #     # Weighted sum of criteria
    #     # These weights can be tuned
    #     return (
    #         3 * era_presence + 
    #         2 * piece_advantage + 
    #         1 * piece_supply + 
    #         1 * piece_centrality + 
    #         1 * era_focus
    #     )
    
    # def _is_winning_move(self, move, board):
    #     """Check if move eliminates opponent from all but one era"""
    #     # Placeholder for win condition logic
    #     pass
    
    # def _evaluate_era_presence(self, board):
    #     """Count number of eras with player's pieces"""
    #     pass
    
    # def _evaluate_piece_advantage(self, board):
    #     """Calculate difference in piece count"""
    #     pass
    
    # def _evaluate_piece_supply(self, board):
    #     """Evaluate remaining pieces in supply"""
    #     pass
    
    # def _evaluate_piece_centrality(self, move):
    #     """Assess how central the move's destination is"""
    #     pass
    
    # def _evaluate_era_focus(self, move, board):
    #     """Evaluate strategic value of next era focus"""
    #     pass

class RandomAIPlayer(PlayerStrategy):
    def getMove(self, board: Board) -> Move:
        """
        Randomly select a valid move from available moves
        """
        
        possible_moves = board.getValidMoves(self)
        return random.choice(possible_moves) if possible_moves else None

class HumanPlayer(PlayerStrategy):
    def getMove(self, board: Board, ) -> Move:

         # If no pieces can move, skip to era selection
        if not board.getValidMoves(self):
            print("No copies to move")
            next_era = self._get_next_era(board)
            if next_era is None:
                return None
            # Return a special move that only changes era
            return Move(None, [], next_era, self._get_opponent_color())
        

        # Select piece
        piece = self._input_piece(board)
        if piece is None:
            return None
        
        # Get move directions
        directions = self._input_directions(board, piece)
        if directions is None:
            return None

        
        # Select next era
        next_era = self._input_next_era(board)
        if next_era is None:
            return None

        return Move(piece, directions, next_era, self._get_opponent_color())
    
    def _input_piece(self, board):
        while True:
            piece_id = input("Select a copy to move\n").strip().upper()

            # Get all pieces on the board for validation
            all_pieces = {}
            for era in [board.past, board.present, board.future]:
                for piece in era.getPieces():
                    # Assuming pieces have an ID property that matches what's shown on board
                    all_pieces[piece.id] = piece

            # Validate piece selection
            if piece_id not in self._pieces:
                print("Not a valid copy\n")
                continue

            selected_piece = all_pieces[piece_id]

            # Check if piece belongs to player
            if selected_piece.owner != self._color:
                print("That is not your copy\n")
                continue

            # Check if piece is in active era
            if selected_piece.position.era != board.current_era:
                print("Cannot select a copy from an inactive era\n")
                continue

            # Check if piece can make any valid moves
            if not board.get_moves_for_piece(selected_piece):
                print("That copy cannot move\n")
                continue

            return selected_piece

    def _input_directions(self, board: 'Board', piece: 'Piece'):
        """Select valid move directions."""
        directions = []
        
        # Handle special case where piece can only make one move
        valid_moves = board.get_moves_for_piece(piece)
        if len(valid_moves) == 1 and len(valid_moves[0].directions) == 1:
            return valid_moves[0].directions

        # First direction
        first_dir = self._get_single_direction(board, piece, "Select the first direction to move: 'n', 'e', 's', 'w', 'f', 'b'\n")
        if first_dir is None:
            return None
        directions.append(first_dir)

        # Second direction
        second_dir = self._get_single_direction(board, piece, "Select the second direction to move: 'n', 'e', 's', 'w', 'f', 'b'\n")
        if second_dir is None:
            return None
        directions.append(second_dir)

        return directions

    def _get_single_direction(self, board: 'Board', piece: 'Piece', prompt: str):
        """Get a single valid direction from user."""
        valid_directions = {'n', 'e', 's', 'w', 'f', 'b'}
        

        while True:
            direction = input(prompt).strip().lower()

            # Check if direction is valid
            if direction not in self.valid_directions:
                print("Not a valid direction\n")
                continue

            # Check if piece can move in that direction
            temp_move = Move(piece, [direction], None, None)
            if not board.is_valid_direction(temp_move):
                print(f"Cannot move {self.direction_full[direction]}\n")
                continue

            return direction
    
    def _input_next_era(self, board: 'Board'):
        """Get valid next era selection."""
        valid_eras = {'past', 'present', 'future'}
        while True:
            era = input("Select the next era to focus on ['past', 'present', 'future']\n").strip().lower()

            if era not in self.valid_eras:
                print("Not a valid era")
                continue

            # Check if selected era is current era
            if era == board.get_era_name(board.current_era):
                print("Cannot select the current era\n")
                continue

            return era