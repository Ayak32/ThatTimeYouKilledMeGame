
class Piece:
    def __init__(self, owner: str):
        self.owner = owner
        self.position = None  # Will be set when placed on board
    


class Board:
    def __init__(self):
        self.past = Era()
        self.present = Era()
        self.future = Era()
        
        # Current focus starts on past era for white player
        self.current_focus = "w_player"
        self.current_era = self.past
        
        self._setupBoard()
    
    def _setupBoard(self):
        """Initialize the board with starting pieces"""
        # Setup Past Era
        self.past.grid[0][0].setPiece(Piece("b_player"))  # Black pieces
        self.past.grid[0][1].setPiece(Piece("b_player"))
        self.past.grid[1][0].setPiece(Piece("b_player"))
        
        self.past.grid[3][3].setPiece(Piece("w_player"))  # White pieces
        self.past.grid[3][2].setPiece(Piece("w_player"))
        self.past.grid[2][3].setPiece(Piece("w_player"))
        
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
    
    def get_moves_for_piece(self, piece):
        """Get all valid moves for a specific piece"""
        valid_moves = []
        # Generate possible moves based on piece position and game rules
        return valid_moves
    
    def is_valid_move(self, move: 'Move') -> bool:
        """Check if a move is valid"""
        # 1. Piece belongs to current player
        if move.piece.owner != self.current_focus:
            return False
        
        # 2. Piece is in current focus era
        if move.piece.position.era != self.current_era:
            return False
        
        # 3. Check if move creates paradox
        if self._creates_paradox(move):
            return False
        
        # 4. Check if destination is valid
        return self._is_valid_destination(move)
    
    def _creates_paradox(self, move: 'Move') -> bool:
        """Check if a move would create a paradox"""
        # Implement paradox checking logic
        pass
    
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
                    if player is None or piece.owner == player:
                        pieces.append(piece)
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