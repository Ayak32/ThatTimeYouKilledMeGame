from movehistory import Move
from position import Position
class Piece:
    def __init__(self, id, owner, position):
        self.id = id
        self.owner = owner
        self.position = None  # Will be set when placed on board
    


class Board:
    def __init__(self):
        self.w_player = None
        self.b_player = None
        self.current_player = None

        self.past = Era("past")
        self.present = Era("present")
        self.future = Era("future")
        
        # Current focus starts on past era for white player
        
        # self.current_era = self.past
        
        # self._setupBoard()
    
    def _setupBoard(self):
        """Initialize the board with starting pieces"""
        # Black pieces setup (top left of each era)
        self.past.grid[0][0].setPiece(self.b_player._pieces[0])    # piece "1"
        self.present.grid[0][0].setPiece(self.b_player._pieces[1]) # piece "2"
        self.future.grid[0][0].setPiece(self.b_player._pieces[2])  # piece "3"
        
        # White pieces setup (bottom right of each era)
        self.past.grid[3][3].setPiece(self.w_player._pieces[0])    # piece "A"
        self.present.grid[3][3].setPiece(self.w_player._pieces[1]) # piece "B"
        self.future.grid[3][3].setPiece(self.w_player._pieces[2])  # piece "C"
        
        # Similar setup for present and future if needed
    
    def makeMove(self, move) -> bool:
        """Execute a move on the board"""
        # First validate the move
        if not self.is_valid_move(move):
            return False
            
        # Execute the move
        return move.execute(self)
    
    def undoMove(self, move: 'Move'):
        """Undo a move on the board"""
        # Implement move reversal
        pass
    
    def getValidMoves(self, player):
        """Get all valid moves for the current player"""
        valid_moves = []
        for piece in player.current_era.getPieces(player):
            valid_moves.extend(self.get_moves_for_piece(piece))
        return valid_moves
    
    # Helper function to calculate new position after a move
    def get_new_position(self, x, y, direction, era=None):
        """Calculate new position after a move, returning None if invalid"""
        new_x = x
        new_y = y
        new_era = era
        
        if direction == 'n':  # North: decrease y (move up)
            new_y -= 1
        elif direction == 's':  # South: increase y (move down)
            new_y += 1
        elif direction == 'e':  # East: increase x (move right)
            new_x += 1
        elif direction == 'w':  # West: decrease x (move left)
            new_x -= 1
        elif direction in ['f', 'b']:
            new_era = self.get_new_era(era, direction)
            if new_era is None:  # Invalid temporal movement
                return None
        
        # Check if new position is within bounds
        if not (0 <= new_x < 4 and 0 <= new_y < 4):
            return None
            
        return (new_x, new_y, new_era)

    # Helper function to get era after time travel
    def get_new_era(self, era, direction):
        """Get new era after temporal movement, respecting temporal movement rules"""
        if direction == 'f':
            if era == self.future:  # Can't move forward from future
                return None
            elif era == self.present:
                return self.future
            elif era == self.past:
                return self.present
        elif direction == 'b':
            if era == self.past:  # Can't move backward from past
                return None
            elif era == self.present:
                return self.past
            elif era == self.future:
                return self.present
        return era

    # Helper function to check if a position is valid
    def is_valid_position(self,x, y):
        return 0 <= x < 4 and 0 <= y < 4

    # Helper function to check if a move would create a paradox
    def creates_paradox(self, x, y, era, piece):
        """Check if placing piece at (x,y) in era would create a paradox"""
        space = era.grid[y][x]
        if space.isOccupied():
            occupied_piece = space.getPiece()
            # Only a paradox if the piece belongs to the same player
            return occupied_piece.owner == piece.owner
        return False

    def get_moves_for_piece(self, piece: 'Piece') -> list:
        """Get all valid moves for a piece"""
        valid_moves = []
        valid_directions = ['n', 's', 'e', 'w', 'f', 'b']
        
        # First check if piece is surrounded by friendlies
        if self.is_surrounded_by_friendlies(piece):
            return []  # Return empty list if surrounded
            
        # Try single moves
        for direction in valid_directions:
            move = Move(piece, [direction], None, None)
            if self.is_valid_direction(move):
                valid_moves.append(move)
        
        # Try double moves
        for dir1 in valid_directions:
            for dir2 in valid_directions:
                move = Move(piece, [dir1, dir2], None, None)
                if self.is_valid_move(move):
                    valid_moves.append(move)
        
        return valid_moves

    def is_surrounded_by_friendlies(self, piece: 'Piece') -> bool:
        """Check if a piece is surrounded by friendly pieces"""
        x, y = piece.position._x, piece.position._y
        era = piece.position._era
        
        # Check all adjacent spaces (north, south, east, west)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            
            # If position is off board, continue
            if not (0 <= new_x < 4 and 0 <= new_y < 4):
                continue
                
            # Get the space and check if it's occupied
            space = era.grid[new_y][new_x]
            if not space.isOccupied():
                return False  # Found an empty space, not surrounded
            
            # Check if occupied by opponent's piece
            if space.getPiece().owner != piece.owner:
                return False  # Found opponent's piece, not surrounded
        
        # If we get here, all valid adjacent spaces are occupied by friendly pieces
        return True

    def get_all_valid_moves(self, player: 'PlayerStrategy') -> dict:
        """Get all valid moves for pieces in the active era"""
        moves_by_piece = {}
        active_pieces = player.current_era.getPieces(player)
        
        for piece in active_pieces:
            valid_moves = self.get_moves_for_piece(piece)
            if valid_moves:  # Only include pieces that can actually move
                moves_by_piece[piece] = valid_moves
        
        return moves_by_piece

    def _getEraByName(self, era_name: str):
        """Get era object by name"""
        era_map = {
            'past': self.past,
            'present': self.present,
            'future': self.future
        }
        return era_map.get(era_name.lower())

    def is_valid_direction(self, move: 'Move') -> bool:
        """Check if a single direction move is valid"""
        if move.piece is None:
            return True
            
        current_pos = move.piece.position
        if current_pos is None:
            return False
            
        direction = move.directions[0]
        result = self.get_new_position(current_pos._x, current_pos._y, direction, current_pos._era)
        
        if result is None:
            return False
            
        new_x, new_y, new_era = result
        
        # Check if moving into own piece (for any direction)
        space = new_era.grid[new_y][new_x]
        if space.isOccupied():
            piece = space.getPiece()
            if piece.owner == move.piece.owner:
                return False
        
        return True

    def is_valid_move(self, move: 'Move') -> bool:
        """Check if a complete move is valid"""
        if move.piece is None:  # Era change only
            return True
            
        current_pos = move.piece.position
        if current_pos is None:
            return False
            
        # Check first direction
        result = self.get_new_position(current_pos._x, current_pos._y, move.directions[0], current_pos._era)
        if result is None:
            return False
            
        # Use the position after first move to check second direction
        if len(move.directions) > 1:
            new_x, new_y, new_era = result
            temp_pos = Position(new_x, new_y, new_era)
            result = self.get_new_position(temp_pos._x, temp_pos._y, move.directions[1], temp_pos._era)
            if result is None:
                return False
                
            new_x, new_y, new_era = result
            # Check final destination
            space = new_era.grid[new_y][new_x]
            if space.isOccupied():
                piece = space.getPiece()
                if move.directions[1] in ['f', 'b']:
                    # Temporal moves are never allowed into occupied spaces
                    return False
                elif piece.owner == move.piece.owner:
                    # Moving into own piece is never valid
                    return False
        
        return True

    def movePiece(self, from_position: Position, to_position: Position) -> bool:
        """Move a piece from one position to another, handling pushing chains"""
        from_space = self.grid[from_position._y][from_position._x]
        to_space = self.grid[to_position._y][to_position._x]
        
        if not from_space.isOccupied():
            return False
        
        moving_piece = from_space.clearPiece()
        
        # If destination is occupied, handle pushing chain
        if to_space.isOccupied():
            # Calculate push direction
            dx = to_position._x - from_position._x
            dy = to_position._y - from_position._y
            
            # Try to push the chain of pieces
            if not self._push_chain(to_position, dx, dy):
                # If push failed, put the original piece back
                from_space.setPiece(moving_piece)
                return False
        
        # Move the piece to its new position
        to_space.setPiece(moving_piece)
        return True

    def _push_chain(self, start_pos: Position, dx: int, dy: int) -> bool:
        """
        Push a chain of pieces in the given direction
        Returns True if push was successful, False if any piece would be pushed off the board
        """
        # First, collect all pieces that need to be pushed
        pieces_to_push = []
        current_pos = start_pos
        
        while True:
            space = self.grid[current_pos._y][current_pos._x]
            if not space.isOccupied():
                break
                
            pieces_to_push.append((space.getPiece(), current_pos))
            
            next_x = current_pos._x + dx
            next_y = current_pos._y + dy
            
            if not (0 <= next_x < 4 and 0 <= next_y < 4):
                # Last piece would be pushed off the board
                if pieces_to_push:
                    last_piece, _ = pieces_to_push[-1]
                    # Remove the piece that would be pushed off
                    self.grid[current_pos._y][current_pos._x].clearPiece()
                return True
            
            current_pos = Position(next_x, next_y, current_pos._era)
        
        # Now execute the pushes in reverse order
        for piece, pos in reversed(pieces_to_push):
            # Clear the current space
            self.grid[pos._y][pos._x].clearPiece()
            
            # Calculate new position
            new_x = pos._x + dx
            new_y = pos._y + dy
            
            # Set piece in new position
            self.grid[new_y][new_x].setPiece(piece)
        
        return True

    # TODO: Implement destination validation logic
    def _is_valid_destination(self, move: 'Move') -> bool:
        """Check if move destination is valid"""
        # Implement destination validation logic
        return True
    
    def isGameOver(self) -> bool:
        """Check if the game is over"""
        # Check if current player has pieces in only one era
        current_player = self.current_player
        eras_with_pieces = 0
        
        for era in [self.past, self.present, self.future]:
            if len(era.getPieces(current_player)) > 0:
                eras_with_pieces += 1
                
        # Game is over if current player has pieces in only one era
        return eras_with_pieces <= 1


    
    # def __hash__(self):
    #     return hash((self._x, self._y, id(self._era)))

class Space:
    def __init__(self, x: int, y: int, era):
        self.position = Position(x, y, era)
        self.adjacent_spaces = []
        self.piece = None
    
    def getAdjacent(self):
        return self.adjacent_spaces
    
    def isOccupied(self) -> bool:
        return self.piece is not None
    
    def getPiece(self):
        return self.piece
    
    def setPiece(self, piece):
        # print("in setPiece. piece: ", piece)
        self.piece = piece
        if piece:
            piece.position = self.position
    
    def clearPiece(self):
        piece = self.piece
        self.piece = None
        return piece

class Era:
    def __init__(self, name):
        self.name = name
        self.grid = [[Space(x, y, self) for x in range(4)]
                    for y in range(4)]
        self._setupAdjacency()
        self._setupInitialPieces()
    
    def _setupAdjacency(self):
        """Set up adjacent spaces for each space in the grid"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # N, S, W, E
        
        for y in range(4):
            for x in range(4):
                current_space = self.grid[y][x]
                
                for dx, dy in directions:
                    new_x, new_y = x + dx, y + dy
                    if 0 <= new_x < 4 and 0 <= new_y < 4:
                        current_space.adjacent_spaces.append(self.grid[new_y][new_x])
    
    def _setupInitialPieces(self):
        """Set up initial piece positions based on era type"""
        # This will be called by the Board class when setting up the game
        pass
    
    def getSpace(self, x: int, y: int):
        """Get space at specific coordinates"""
        if 0 <= x < 4 and 0 <= y < 4:
            return self.grid[y][x]
        return None
    
    def getPieces(self, player=None):
        """Get all pieces in this era, optionally filtered by player"""
        pieces = []
        for row in self.grid:
            for space in row:
                if space.isOccupied():
                    piece = space.getPiece()
                    # print(f"{piece.id}, {piece.owner}, {piece.position}")
                    # print(player._color)
                    if player is None or piece.owner == player._color:
                        # print("appending piece")
                        pieces.append(piece)
        # print(pieces)
        return pieces
    
    def movePiece(self, from_position: Position, to_position: Position) -> bool:
        """Move a piece from one position to another, handling pushing chains"""
        from_space = self.grid[from_position._y][from_position._x]
        to_space = self.grid[to_position._y][to_position._x]
        
        if not from_space.isOccupied():
            return False
        
        moving_piece = from_space.clearPiece()
        
        # If destination is occupied, handle pushing chain
        if to_space.isOccupied():
            # Calculate push direction
            dx = to_position._x - from_position._x
            dy = to_position._y - from_position._y
            
            # Try to push the chain of pieces
            if not self._push_chain(to_position, dx, dy):
                # If push failed, put the original piece back
                from_space.setPiece(moving_piece)
                return False
        
        # Move the piece to its new position
        to_space.setPiece(moving_piece)
        return True

    def _push_chain(self, start_pos: Position, dx: int, dy: int) -> bool:
        """
        Push a chain of pieces in the given direction
        Returns True if push was successful, False if any piece would be pushed off the board
        """
        # First, collect all pieces that need to be pushed
        pieces_to_push = []
        current_pos = start_pos
        
        while True:
            space = self.grid[current_pos._y][current_pos._x]
            if not space.isOccupied():
                break
                
            pieces_to_push.append((space.getPiece(), current_pos))
            
            next_x = current_pos._x + dx
            next_y = current_pos._y + dy
            
            if not (0 <= next_x < 4 and 0 <= next_y < 4):
                # Last piece would be pushed off the board
                if pieces_to_push:
                    last_piece, _ = pieces_to_push[-1]
                    # Remove the piece that would be pushed off
                    self.grid[current_pos._y][current_pos._x].clearPiece()
                return True
            
            current_pos = Position(next_x, next_y, current_pos._era)
        
        # Now execute the pushes in reverse order
        for piece, pos in reversed(pieces_to_push):
            # Clear the current space
            self.grid[pos._y][pos._x].clearPiece()
            
            # Calculate new position
            new_x = pos._x + dx
            new_y = pos._y + dy
            
            # Set piece in new position
            self.grid[new_y][new_x].setPiece(piece)
        
        return True