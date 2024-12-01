from position import Position
from copy import deepcopy
import copy

class Originator:
    """Manages the game state that needs to be saved and restored"""
    def __init__(self, game):
        self._state = game
    
    def save(self):
        """Creates a memento containing a deep copy of current state"""
        game_copy = type(self._state)()
        
        # Deep copy the board first
        game_copy.board = copy.deepcopy(self._state.board)
        
        # Deep copy players and their states
        game_copy.w_player = copy.deepcopy(self._state.w_player)
        game_copy.b_player = copy.deepcopy(self._state.b_player)
        
        # Ensure all piece references are properly maintained
        for player in [game_copy.w_player, game_copy.b_player]:
            # Fix supply pieces
            for piece in player._supply:
                piece.owner = player._color
            
            # Fix active pieces
            for piece in player._pieces:
                piece.owner = player._color
            
            # Ensure supply tracking is preserved
            player._activated_pieces = copy.deepcopy(player._activated_pieces)
            player._supply = copy.deepcopy(player._supply)
            player._pieces = copy.deepcopy(player._pieces)
        
        # Copy other game state
        game_copy.current_player = game_copy.w_player if self._state.current_player == self._state.w_player else game_copy.b_player
        game_copy.turn_number = self._state.turn_number
        game_copy.state = self._state.state
        
        # Make sure the current_era references point to the new board's eras
        game_copy.w_player.current_era = game_copy.board.past if self._state.w_player.current_era == self._state.board.past else \
                                        game_copy.board.present if self._state.w_player.current_era == self._state.board.present else \
                                        game_copy.board.future
        
        game_copy.b_player.current_era = game_copy.board.past if self._state.b_player.current_era == self._state.board.past else \
                                        game_copy.board.present if self._state.b_player.current_era == self._state.board.present else \
                                        game_copy.board.future
        
        return Memento(game_copy)
    
    def restore(self, memento):
        """Restores state from a memento"""
        restored_state = memento.get_state()
        return restored_state

class Memento:
    """Stores and protects the game state"""
    def __init__(self, state):
        self._state = state
    
    def get_state(self):
        return self._state

class Caretaker:
    """Manages the history of game states"""
    def __init__(self, originator):
        self._mementos = []
        self._originator = originator
        self._head = -1
    
    def save(self):
        """Saves current state and updates history"""
        # Truncate any future states when saving after an undo
        if self._head < len(self._mementos) - 1:
            self._mementos = self._mementos[:self._head + 1]
        
        # Save new state
        self._mementos.append(self._originator.save())
        self._head += 1
    
    def undo(self):
        """Restores previous state"""
        if self._head <= 0:
            return None
        
        self._head -= 1
        return self._mementos[self._head].get_state()
    
    def redo(self):
        """Restores next state"""
        if self._head >= len(self._mementos) - 1:
            return None
        
        self._head += 1
        return self._mementos[self._head].get_state()
    
    def next(self):
        """Prepares for next move by ensuring we're at latest state"""
        self._mementos = self._mementos[:self._head + 1]
        memento = copy.deepcopy(self._mementos[-1])
        self._originator.restore(memento)
        return memento.get_state()

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

    def __str__(self):
        """String representation of the move"""
        if self.piece is None:
            next_era_name = self.next_era.name if self.next_era else "None"
            return f"Selected move: None,None,None,{next_era_name}"
        else:
            next_era_name = self.next_era.name if self.next_era else "None"
            return f"Selected move: {self.piece.id},{','.join(self.directions)},{next_era_name}"
