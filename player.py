from abc import ABC, abstractmethod
from board import Board
from movehistory import Move
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
        _pieces = [1]
        _color = color
        _supply = 4

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
        # piece = self._select_piece(board)
        # directions = self._select_directions(piece)
        # next_era = self._select_next_era(board)
        # return Move(piece, directions, next_era)
        pass