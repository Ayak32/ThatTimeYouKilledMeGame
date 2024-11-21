from position import Position
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



# class Move:
#     def __init__(self, piece, directions, next_era, player):
#         self.piece = piece
#         self.directions = directions
#         self.next_era = next_era
#         self.player = player
#     def execute(self, board):
#         # Move piece through specified directions
#         for direction in self.directions:
#             self.piece.move(direction)
        
#         # Update piece's era
#         self.piece.current_era = board.get_era_by_name(self.next_era)
        
#         # Update board focus
#         board.current_player = self.piece.owner
#         board.current_era = board.get_era_by_name(self.next_era)
    
#     def undo(self, board):
#         # Reverse the move
#         # Move piece back
#         # Restore previous era and focus
#         pass


# In movehistory.py
class Move:
    def __init__(self, piece, directions, next_era, next_player):
        self.piece = piece
        self.directions = directions
        self.next_era = next_era
        self.next_player = next_player
    
    def execute(self, board: 'Board') -> bool:
        """
        Execute the move on the board
        Returns True if successful, False otherwise
        """
        # Handle special case of era-change-only move
        if self.piece is None:
            board.current_player.current_era = board._getEraByName(self.next_era)
            board.current_player = self.next_player

            return True

        current_pos = self.piece.position
        current_era = current_pos._era

        # Execute each direction
        for direction in self.directions:
            new_pos = self._get_new_position(current_pos, direction, board)
            if new_pos is None:
                return False
                
            # If it's a temporal move, get the new era
            if direction in ['f', 'b']:
                new_era = self._get_new_era(current_era, direction, board)
                if new_era is None:
                    return False
                success = new_era.movePiece(current_pos, new_pos)
            else:
                success = current_era.movePiece(current_pos, new_pos)
            
            if not success:
                return False
                
            # Update for next direction
            current_pos = new_pos
            current_era = current_pos._era

        # Update board focus for next turn
        board.current_player.current_era = board._getEraByName(self.next_era)
        board.current_player = self.next_player
        
        return True

    def _get_new_position(self, current_pos: 'Position', direction: str, board: 'Board'):
        """Calculate new position after a move in given direction"""
        new_x, new_y = current_pos._x, current_pos._y
        
        if direction == 'n':
            new_y -= 1
        elif direction == 's':
            new_y += 1
        elif direction == 'e':
            new_x += 1
        elif direction == 'w':
            new_x -= 1
            
        # For temporal moves, position stays the same
        if direction in ['f', 'b']:
            return Position(current_pos._x, current_pos._y, current_pos._era)
            
        # Check bounds
        if 0 <= new_x < 4 and 0 <= new_y < 4:
            return Position(new_x, new_y, current_pos._era)
        return None

    def _get_new_era(self, current_era: 'Era', direction: str, board: 'Board'):
        """Get new era for temporal movement"""
        if direction == 'f':
            if current_era == board.past:
                return board.present
            elif current_era == board.present:
                return board.future
        elif direction == 'b':
            if current_era == board.future:
                return board.present
            elif current_era == board.present:
                return board.past
        return None

    def __str__(self) -> str:
        """String representation for move output"""
        if self.piece is None:
            return f"no_move,{self.next_era}"
        return f"{self.piece.id},{','.join(self.directions)},{self.next_era}"





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