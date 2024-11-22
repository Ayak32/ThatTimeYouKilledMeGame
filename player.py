from abc import ABC, abstractmethod
from board import Board
from movehistory import Move
from position import Position
from board import Piece
import random

class PlayerFactory:
    """
    Factory for creating player strategies
    Supports different player types for each color
    """
    @staticmethod
    def create_player(player_type, color, board):
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
        return player_class(color, board)
    



""" Strategy Pattern """

class PlayerStrategy(ABC):
    def __init__(self, color, board) -> None:
        self._color = color
        
        if color == "b_player":
            self.current_era = board.future
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
            self.current_era = board.past
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
        # Find the piece in supply with matching ID
        for piece in self._supply:
            if piece.id == piece_id:
                self._supply.remove(piece)
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
    def getMove(self, board):
        """
        Randomly select a valid move from available moves
        """
        
        possible_moves = board.getValidMoves(self)
        return random.choice(possible_moves) if possible_moves else None

class HumanPlayer(PlayerStrategy):
    def getMove(self, board: 'Board') -> Move:
        """Get move from human player input"""
        # Get valid moves for all pieces in current era
        valid_moves = {}
        max_directions = 1
        
        # Get pieces in current era
        pieces = self.current_era.getPieces(self)
        if not pieces:
            print("No copies to move")
            next_era = self._input_next_era(board)
            return Move(None, [], next_era, 
                       "b_player" if self._color == "w_player" else "w_player")
        
        # Get valid moves for each piece
        for piece in pieces:
            piece_moves = board.get_moves_for_piece(piece)
            if piece_moves:  # Only include pieces that can actually move
                valid_moves[piece] = piece_moves
                max_directions = max(max_directions, 
                                   max(len(move.directions) for move in piece_moves))
        
        # If no pieces can move
        if not valid_moves:
            print("No copies to move")
            next_era = self._input_next_era(board)
            return Move(None, [], next_era, 
                       "b_player" if self._color == "w_player" else "w_player")
        
        # Get piece selection from user
        piece = self._input_piece(board, valid_moves)
        if piece is None:
            return None
        
        # Special case: only one piece can move and it can only make one move
        if (len(valid_moves) == 1 and 
            len(valid_moves[piece]) == 1 and 
            len(valid_moves[piece][0].directions) == 1):
            directions = valid_moves[piece][0].directions
        else:
            directions = self._input_directions(board, piece, max_directions)
            if not directions:
                return None
        
        next_era = self._input_next_era(board)
        return Move(piece, directions, next_era, 
                   "b_player" if self._color == "w_player" else "w_player")

    def _input_piece(self, board: 'Board', valid_moves: dict) -> 'Piece':
        """Get valid piece selection from user."""
        while True:
            piece_id = input("Select a copy to move\n").strip().upper()
            
            # First check if piece exists in any era
            piece_found = False
            for piece in self.current_era.getPieces(self):
                if piece.id == piece_id:
                    piece_found = True
                    break
            
            # If piece wasn't found in current era, check other eras
            if not piece_found:
                for era in [board.past, board.present, board.future]:
                    if era != self.current_era:
                        for piece in era.getPieces(self):
                            if piece.id == piece_id and piece.owner == self._color:
                                print("Cannot select a copy from an inactive era")
                                piece_found = True
                                break
                    if piece_found:
                        break
                
                if not piece_found:
                    print("Not a valid copy")
                continue
            
            # Now check if the piece is in valid moves
            selected_piece = None
            for piece in valid_moves.keys():
                if piece.id == piece_id:
                    selected_piece = piece
                    break
            
            if not selected_piece:
                print("That copy cannot move")
                continue
            
            # Check if piece can make moves of maximum length
            max_move_length = max(len(move.directions) for moves in valid_moves.values() 
                                for move in moves)
            piece_max_length = max(len(move.directions) for move in valid_moves[selected_piece])
            
            if piece_max_length < max_move_length:
                print("That copy cannot move")
                continue
                
            return selected_piece

    def _input_directions(self, board: 'Board', piece: 'Piece', max_directions: int):
        """Select valid move directions."""
        valid_directions = {'n', 's', 'e', 'w', 'f', 'b'}
        directions = []
        
        # Get valid moves for this piece
        valid_moves = board.get_moves_for_piece(piece)
        
        # If piece can only make shorter moves than others, it can't be used
        if max(len(move.directions) for move in valid_moves) < max_directions:
            print("That copy cannot move")
            return None
            
        # Get first direction
        while True:
            direction = input("Select first direction to move ['n', 's', 'e', 'w', 'f', 'b']\n").strip().lower()
            if direction not in valid_directions:
                print("Not a valid direction")
                continue
                
            # Check if this is a valid first move
            temp_move = Move(piece, [direction], None, None)
            if not board.is_valid_direction(temp_move):
                print("Not a valid direction")
                continue
                
            directions.append(direction)
            break
        
        # If two moves are possible, get second direction
        if max_directions > 1:
            while True:
                direction = input("Select second direction to move ['n', 's', 'e', 'w', 'f', 'b']\n").strip().lower()
                if direction not in valid_directions:
                    print("Not a valid direction")
                    continue
                    
                # Check if complete move is valid
                temp_move = Move(piece, directions + [direction], None, None)
                if not board.is_valid_move(temp_move):
                    print("Invalid move")
                    continue
                    
                directions.append(direction)
                break
        
        return directions

    def _input_next_era(self, board: 'Board'):
        """Get valid next era selection."""
        valid_eras = {'past', 'present', 'future'}
        while True:
            era = input("Select the next era to focus on ['past', 'present', 'future']\n").strip().lower()

            if era not in valid_eras:
                print("Not a valid era")
                continue

            # Get the actual Era object instead of using the string
            next_era = getattr(board, era)  # This gets board.past, board.present, or board.future
            
            # Check if selected era is current era
            if next_era == self.current_era:
                print("Cannot select the current era")
                continue

            return next_era  # Return the Era object instead of the string