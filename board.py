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

    def get_moves_for_piece(self, piece):
        """Get all valid moves for a specific piece"""
        if piece is None or piece.position is None:
            return []

        valid_moves = []
        basic_directions = ['n', 's', 'e', 'w']
        time_directions = ['f', 'b']
        
        # Get current position details
        curr_x = piece.position._x
        curr_y = piece.position._y
        curr_era = piece.position._era


        # First moves (spatial or temporal)
        first_directions = basic_directions + time_directions
        for first_dir in first_directions:
            # Handle spatial movement
            if first_dir in basic_directions:
                result = self.get_new_position(curr_x, curr_y, first_dir, curr_era)
                if result is None:
                    continue
                new_x, new_y, new_era = result
                
                # Check if move is valid
                if not self.is_valid_position(new_x, new_y):
                    continue
                if self.creates_paradox(new_x, new_y, new_era, piece):
                    continue
                
                # Now check second moves from this new position
                second_directions = basic_directions + time_directions
                for second_dir in second_directions:
                    if second_dir in basic_directions:
                        result = self.get_new_position(new_x, new_y, second_dir, new_era)
                        if result is None:
                            continue
                        final_x, final_y, final_era = result
                    else:  # time travel
                        final_x, final_y = new_x, new_y
                        final_era = self.get_new_era(new_era, second_dir)
                    
                    if (final_era and self.is_valid_position(final_x, final_y) and 
                        not self.creates_paradox(final_x, final_y, final_era, piece)):
                        # Check available focus eras (not current era)
                        for next_focus in ['past', 'present', 'future']:
                            if next_focus != self.current_player.current_era:
                                move = Move(piece, [first_dir, second_dir], next_focus, 
                                         "b_player" if piece.owner == "w_player" else "w_player")
                                valid_moves.append(move)

            # Handle time travel as first move
            else:
                new_x, new_y = curr_x, curr_y
                new_era = self.get_new_era(curr_era, first_dir)
                if not new_era or self.creates_paradox(new_x, new_y, new_era, piece):
                    continue
                
                # Second moves must be spatial after time travel
                for second_dir in basic_directions:
                    result = self.get_new_position(new_x, new_y, second_dir, new_era)
                    if result is None:
                        continue
                    final_x, final_y, final_era = result
                    
                    if (self.is_valid_position(final_x, final_y) and 
                        not self.creates_paradox(final_x, final_y, new_era, piece)):
                        # Check available focus eras
                        for next_focus in ['past', 'present', 'future']:
                            if next_focus != self.current_player.current_era:
                                move = Move(piece, [first_dir, second_dir], next_focus,
                                         "b_player" if piece.owner == "w_player" else "w_player")
                                valid_moves.append(move)

        return valid_moves

    def _getEraByName(self, era_name: str):
        """Get era object by name"""
        era_map = {
            'past': self.past,
            'present': self.present,
            'future': self.future
        }
        return era_map.get(era_name.lower())

    def is_valid_direction(self, move: 'Move') -> bool:
        """Check if a move's direction is valid"""
        if not move.piece or not move.directions:
            return False
            
        current_pos = move.piece.position
        
        # For single direction validation (from _get_single_direction)
        if len(move.directions) == 1:
            direction = move.directions[0]
            
            # Check if trying to move backward with empty supply
            if direction == 'b' and not self.current_player._supply:
                return False
                
            # Get new position after move
            result = self.get_new_position(current_pos._x, current_pos._y, direction, current_pos._era)
            if result is None or not self.is_valid_position(result[0], result[1]):
                return False
                
            # For spatial moves, check current era
            if direction not in ['f', 'b']:
                space = current_pos._era.grid[result[1]][result[0]]
                if space.isOccupied() and space.getPiece().owner == move.piece.owner:
                    return False
            
            return True
            
        # For full two-direction move validation
        first_dir, second_dir = move.directions
        
        # Get position after first move
        result1 = self.get_new_position(current_pos._x, current_pos._y, first_dir, current_pos._era)
        if result1 is None or not self.is_valid_position(result1[0], result1[1]):
            return False
            
        # Check first move in current era
        if first_dir not in ['f', 'b']:
            space1 = current_pos._era.grid[result1[1]][result1[0]]
            if space1.isOccupied() and space1.getPiece().owner == move.piece.owner:
                return False
        
        # Get position after second move
        result2 = self.get_new_position(result1[0], result1[1], second_dir, result1[2])
        if result2 is None or not self.is_valid_position(result2[0], result2[1]):
            return False
            
        # Check final position in destination era
        final_space = result2[2].grid[result2[1]][result2[0]]
        if final_space.isOccupied() and final_space.getPiece().owner == move.piece.owner:
            return False
            
        return True

    def is_valid_move(self, move):
        """Validate if a move is legal"""
        # Handle era-change-only moves
        if move.piece is None:
            return True
            
        # For moves with pieces, validate ownership and other rules
        if move.piece.owner != self.current_player._color:
            return False
            
        # Validate each direction in the move
        current_pos = move.piece.position
        for direction in move.directions:
            if not self.is_valid_direction(move):
                return False
            result = self.get_new_position(current_pos._x, current_pos._y, direction, current_pos._era)
            if result is None:
                return False
            new_x, new_y, new_era = result
            if not self.is_valid_position(new_x, new_y):
                return False
            current_pos = Position(new_x, new_y, new_era)
            
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
        """Move a piece from one position to another"""
        from_space = self.grid[from_position._y][from_position._x]
        to_space = self.grid[to_position._y][to_position._x]
        
        if not from_space.isOccupied():
            return False
        
        moving_piece = from_space.clearPiece()
        
        # Handle capture if destination is occupied
        if to_space.isOccupied():
            captured_piece = to_space.getPiece()
            # Only allow capture of opponent's pieces
            if captured_piece.owner == moving_piece.owner:
                # Put the piece back if trying to capture own piece
                from_space.setPiece(moving_piece)
                return False
            # Clear the captured piece
            to_space.clearPiece()
        
        # Move the piece to its new position
        to_space.setPiece(moving_piece)
        return True