from abc import ABC, abstractmethod
from board import Board
from movehistory import Move


""" Strategy Pattern """

class Player(ABC):
    def __init__(self, color) -> None:
        _pieces = [1]
        _color = color
        _supply = 4

    @abstractmethod
    def getMove(self, board: Board) -> Move:
        pass

class HeuristicAIPlayer(Player):
    def getMove(self, board: Board) -> Move:
        valid_moves = board.getValidMoves(self)
        best_move = None
        best_score = float('-inf')
        for move in valid_moves:
            score = self._calculateScore(move)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move
    
    def calculateScore(self, move):
        pass
class RandomAIPlayer(Player):
    def getMove(self, board: Board) -> Move:
        pass

class HumanPlayer(Player):
    def getMove(self, board: Board) -> Move:
        pass