
class MoveHistory():
    def __init__(self):
        moves = [] # stack of moves
        undoneMove = [] # stack of moves
    
    def addMove(move):
        pass

    def undo():
        pass
    
    def redo():
        pass



class Move:
    def __init__(self, piece, directions, next_era, player):
        self.piece = piece
        self.directions = directions
        self.next_era = next_era
        self.player = player
    def execute(self, board):
        # Move piece through specified directions
        for direction in self.directions:
            self.piece.move(direction)
        
        # Update piece's era
        self.piece.current_era = board.get_era_by_name(self.next_era)
        
        # Update board focus
        board.current_focus = self.piece.owner
        board.current_era = board.get_era_by_name(self.next_era)
    
    def undo(self, board):
        # Reverse the move
        # Move piece back
        # Restore previous era and focus
        pass







# class GameMemento:
#     def __init__(self, board_state, turn_number, current_player):
#         self.board_state = copy.deepcopy(board_state)
#         self.turn_number = turn_number
#         self.current_player = current_player

# class GameHistory:
#     def __init__(self):
#         self.history = []
#         self.current_index = -1
    
#     def save_state(self, board):
#         # Create a memento of current game state
#         memento = GameMemento(board, self.turn_number, self.current_player)
        
#         # If we're not at the latest state, truncate future history
#         if self.current_index < len(self.history) - 1:
#             self.history = self.history[:self.current_index + 1]
        
#         self.history.append(memento)
#         self.current_index += 1
    
#     def undo(self):
#         # Move back in history
#         if self.current_index > 0:
#             self.current_index -= 1
#             return self.history[self.current_index]
    
#     def redo(self):
#         # Move forward in history
#         if self.current_index < len(self.history) - 1:
#             self.current_index += 1
#             return self.history[self.current_index]