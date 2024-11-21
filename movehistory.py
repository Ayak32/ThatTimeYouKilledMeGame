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
            board.current_player.current_era = self.next_era
            board.current_player = board.b_player if self.next_player == "b_player" else board.w_player
            return True

        current_pos = self.piece.position
        current_era = current_pos._era

        # Execute each direction
        for direction in self.directions:
            new_pos = self._get_new_position(current_pos, direction, board)
            if new_pos is None:
                return False
                
            # Move the piece
            if direction in ['f', 'b']:
                # Clear piece from current position in old era
                current_era.grid[current_pos._y][current_pos._x].clearPiece()
                
                # If moving backward in time and player has supply, spawn a new piece
                if direction == 'b' and board.current_player._supply:
                    # Get the first piece from supply
                    supply_piece = board.current_player._supply[0]
                    activated_piece = board.current_player.activate_piece(supply_piece.id)
                    if activated_piece:
                        # Place the new piece in the original position
                        current_era.grid[current_pos._y][current_pos._x].setPiece(activated_piece)
                
                # Set piece in new position in new era
                new_pos._era.grid[new_pos._y][new_pos._x].setPiece(self.piece)
            else:
                success = current_era.movePiece(current_pos, new_pos)
                if not success:
                    return False
            
            # Update for next direction
            current_pos = new_pos
            current_era = new_pos._era

        # Update board focus for next turn
        board.current_player.current_era = self.next_era
        board.current_player = board.b_player if board.current_player == board.w_player else board.w_player
        
        return True

    def _get_new_position(self, current_pos: 'Position', direction: str, board: 'Board'):
        """Calculate new position after a move in given direction"""
        result = board.get_new_position(current_pos._x, current_pos._y, direction, current_pos._era)
        if result is None:
            return None
        new_x, new_y, new_era = result
        return Position(new_x, new_y, new_era)

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

    # def _get_era_name(self, era: 'Era') -> str:
    #     """Convert Era object to its string name representation"""
    #     if era == era.board.past:
    #         return "past"
    #     elif era == era.board.present:
    #         return "present"
    #     elif era == era.board.future:
    #         retubrn "future"
    #     return "unknown"

    def __str__(self):
        """String representation of the move"""
        if self.piece is None:
            # Era-change-only move
            return f"Change focus to {self.next_era.name}"
        else:
            # Normal move with piece
            return f"{self.piece.id},{','.join(self.directions)},{self.next_era.name}"

    # def _getNameByEra(self, era_name: str):
    #     """Get era object by name"""
    #     era_map = {
    #         'past': self.past,
    #         'present': self.present,
    #         'future': self.future
    #     }
    #     return era_map.get(era_name.lower())



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