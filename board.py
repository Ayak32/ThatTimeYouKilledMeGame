from movehistory import Move

class Piece:
    def __init__(self, id, owner, position):
        self.id = id
        self.owner = owner
        self.position = None  # Will be set when placed on board
    


class Board:
    def __init__(self, white_player, black_player):
        self.w_player = white_player
        self.b_player = black_player

        self.past = Era()
        self.present = Era()
        self.future = Era()
        
        # Current focus starts on past era for white player
        self.current_focus = "w_player"
        self.current_era = self.past
        
        self._setupBoard()
    
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
    
    def makeMove(self, move: 'Move') -> bool:
        """Execute a move on the board"""
        if not self.is_valid_move(move):
            return False
        
        # Execute the move steps
        current_pos = move.piece.position
        for direction in move.directions:
            if not self._executeStep(current_pos, direction):
                return False
            current_pos = move.piece.position
        
        # Update focus
        self.current_focus = move.next_player
        self.current_era = self._getEraByName(move.next_era)
        return True
    
    def undoMove(self, move: 'Move'):
        """Undo a move on the board"""
        # Implement move reversal
        pass
    
    def getValidMoves(self, player):
        """Get all valid moves for a player"""
        moves = []
        for piece in self.current_era.getPieces(player):
            moves.extend(self.get_moves_for_piece(piece))
        return moves
    
    # Helper function to calculate new position after a move
    def get_new_position(self, x, y, direction):
        if direction == 'n':
            return (x - 1, y)
        elif direction == 's':
            return (x + 1, y)
        elif direction == 'e':
            return (x, y + 1)
        elif direction == 'w':
            return (x, y - 1)
        return (x, y)  # For time travel directions

    # Helper function to get era after time travel
    def get_new_era(self, era, direction):
        if direction == 'f':
            if era == self.past:
                return self.present
            elif era == self.present:
                return self.future
            return None
        elif direction == 'b':
            if era == self.future:
                return self.present
            elif era == self.present:
                return self.past
            return None
        return era

    # Helper function to check if a position is valid
    def is_valid_position(self,x, y):
        return 0 <= x < 4 and 0 <= y < 4

    # Helper function to check if a move would create a paradox
    def creates_paradox(self, new_x, new_y, new_era, piece):
        if new_era.grid[new_y][new_x].isOccupied():
            target_piece = new_era.grid[new_y][new_x].getPiece()
            return target_piece.owner == piece.owner
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
                new_x, new_y = self.get_new_position(curr_x, curr_y, first_dir)
                new_era = curr_era
                
                # Check if move is valid
                if not self.is_valid_position(new_x, new_y):
                    continue
                if self.creates_paradox(new_x, new_y, new_era, piece):
                    continue
                
                # Now check second moves from this new position
                second_directions = basic_directions + time_directions
                for second_dir in second_directions:
                    if second_dir in basic_directions:
                        final_x, final_y = self.get_new_position(new_x, new_y, second_dir)
                        final_era = new_era
                    else:  # time travel
                        final_x, final_y = new_x, new_y
                        final_era = self.get_new_era(new_era, second_dir)
                    
                    if (final_era and self.is_valid_position(final_x, final_y) and 
                        not self.creates_paradox(final_x, final_y, final_era, piece)):
                        # Check available focus eras (not current era)
                        for next_focus in ['past', 'present', 'future']:
                            if self._getEraByName(next_focus) != self.current_era:
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
                    final_x, final_y = self.get_new_position(new_x, new_y, second_dir)
                    if (self.is_valid_position(final_x, final_y) and 
                        not self.creates_paradox(final_x, final_y, new_era, piece)):
                        # Check available focus eras
                        for next_focus in ['past', 'present', 'future']:
                            if self._getEraByName(next_focus) != self.current_era:
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

    def is_valid_direction(self, move: Move) -> bool:
        """Check if a single direction move is valid"""
        piece = move.piece
        direction = move.directions[0]
        
        # Get current position
        current_pos = piece.position
        
        # Calculate new position based on direction
        new_pos = self.get_new_position(current_pos._x, current_pos._y, direction)
        
        # Check bounds and collisions
        if not self.is_valid_position(new_pos[0], new_pos[1]):
            return False
            
        # Check for paradox
        if self.creates_paradox(new_pos[0], new_pos[1], piece.position._era, piece):
            return False
        
        return True


    
    def is_valid_move(self, move: 'Move') -> bool:
        """Check if a move is valid"""
        # 1. Piece belongs to current player
        if move.piece.owner != self.current_focus:
            return False
        
        # 2. Piece is in current focus era
        if move.piece.position.era != self.current_era:
            return False
        
        # 3. Check if move creates paradox
        if self.creates_paradox(move):
            return False
        
        # 4. Check if destination is valid
        return self._is_valid_destination(move)

    
    def _is_valid_destination(self, move: 'Move') -> bool:
        """Check if move destination is valid"""
        # Implement destination validation logic
        pass
    
    def isGameOver(self) -> bool:
        """Check if the game is over"""
        # Check if either player has pieces in only one era
        for player in ["w_player", "b_player"]:
            eras_with_pieces = 0
            for era in [self.past, self.present, self.future]:
                if era.getPieces(player):
                    eras_with_pieces += 1
            if eras_with_pieces <= 1:
                return True
        return False

class Position:
    def __init__(self, x: int, y: int, era):
        self._x = x
        self._y = y
        self._era = era

    
    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return (self._x == other._x and 
                self._y == other._y and 
                self._era == other._era)
    
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
    def __init__(self):
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
        from_space = self.grid[from_position.y][from_position.x]
        to_space = self.grid[to_position.y][to_position.x]
        
        if not from_space.isOccupied():
            return False
        
        piece = from_space.clearPiece()
        # Handle capture if destination is occupied
        if to_space.isOccupied():
            captured_piece = to_space.clearPiece()
            # You might want to handle the captured piece here
        
        to_space.setPiece(piece)
        return True