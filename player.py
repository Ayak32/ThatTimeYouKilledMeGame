from abc import ABC, abstractmethod
from board import Board
from movehistory import Move
from position import Position
from board import Piece
import random

class PlayerFactory:
    """
    Factory for creating player strategies
    Supports different player types for each color
    """
    @staticmethod
    def create_player(player_type, color, board):
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
        return player_class(color, board)
    



""" Strategy Pattern """

class PlayerStrategy(ABC):
    def __init__(self, color, board) -> None:
        self._color = color
        
        if color == "b_player":
            self.current_era = board.future
            self._pieces = [
            Piece("1", color, None),
            Piece("2", color, None),
            Piece("3", color, None)
            ]

            self._supply = [
            Piece("4", color, None),
            Piece("5", color, None),
            Piece("6", color, None),
            Piece("7", color, None)]
        else:
            self.current_era = board.past
            self._pieces = [
            Piece("A", color, None),
            Piece("B", color, None),
            Piece("C", color, None)]

            self._supply = [Piece("D", color, None),
            Piece("E", color, None),
            Piece("F", color, None),
            Piece("G", color, None)]
 

    def activate_piece(self, piece_id: str):
        """Move a piece from supply to active pieces"""
        # Find the piece in supply with matching ID
        for piece in self._supply:
            if piece.id == piece_id:
                self._supply.remove(piece)
                self._pieces.append(piece)
                return piece
        return None

    def deactivate_piece(self, piece: Piece):
        """Move a piece from active to supply"""
        if piece in self._pieces:
            self._pieces.remove(piece)
            self._supply.append(piece.name)
    
    @abstractmethod
    def getMove(self, board: Board) -> Move:
        pass

class HeuristicAIPlayer(PlayerStrategy):
    def getMove(self, board: 'Board') -> Move:
        """Get the best move based on heuristic evaluation"""
        valid_moves = board.getValidMoves(self)
        
        # Calculate and display current scores for both players
        # Only display if both players are AI
        if board.score and (isinstance(board.w_player, (HeuristicAIPlayer, RandomAIPlayer)) and 
                          isinstance(board.b_player, (HeuristicAIPlayer, RandomAIPlayer))):
            # Always display white's score first
            board.game._display_scores(board.w_player, "white")
            board.game._display_scores(board.b_player, "black")
        
        # If no valid moves, just change era
        if not valid_moves:
            next_era = self._get_best_era(board)
            return Move(None, [], next_era, self._color)
        
        # Find best move using heuristic
        best_move = None
        best_score = float('-inf')
        
        for move in valid_moves:
            # Ensure move has a next era selected
            if move.next_era is None:
                move.next_era = self._get_best_era(board)
            
            # Simulate the move
            original_pos = move.piece.position if move.piece else None
            success = move.execute(board)
            
            if success:
                # Check if this is a winning move
                opponent = board.b_player if self._color == "w_player" else board.w_player
                if self._evaluate_era_presence(board) <= 1:
                    score = 9999
                else:
                    # Calculate weighted sum
                    score = (3 * self._evaluate_era_presence(board) + 
                            2 * HeuristicAIPlayer._evaluate_piece_advantage(board, self) + 
                            1 * len(self._supply) + 
                            1 * HeuristicAIPlayer._evaluate_centrality(board, self) + 
                            1 * self._evaluate_focus(board, move.next_era))
                
                # Undo the move simulation
                self._undo_move(board, move, original_pos)
                
                # Update best move if this score is higher
                if score > best_score:
                    best_score = score
                    best_move = move
                elif score == best_score and random.random() < 0.5:
                    # Randomly break ties
                    best_move = move
        
        # Ensure the best move has a next era selected
        if best_move and best_move.next_era is None:
            best_move.next_era = self._get_best_era(board)
            
        return best_move

    def _count_eras_with_pieces(self, board: 'Board', player: 'PlayerStrategy') -> int:
        """Count number of eras containing player's pieces"""
        count = 0
        for era in [board.past, board.present, board.future]:
            if len(era.getPieces(player)) > 0:
                count += 1
        return count

    @staticmethod
    def _evaluate_piece_advantage(board: 'Board', player) -> int:
        """Evaluate piece advantage (positive = advantage, negative = disadvantage)"""
        opponent = board.b_player if player._color == "w_player" else board.w_player
        return len(player._pieces) - len(opponent._pieces)

    @staticmethod
    def _evaluate_centrality(board: 'Board', player) -> int:
        """Evaluate how many pieces are in central positions"""
        centrality = 0
        for era in [board.past, board.present, board.future]:
            for piece in era.getPieces(player):
                x, y = piece.position._x, piece.position._y
                # Center positions (1,1), (1,2), (2,1), (2,2) are worth 1 point
                if 0 < x < 3 and 0 < y < 3:
                    centrality += 1
        return centrality

    def _evaluate_era_presence(self, board: 'Board') -> int:
        """Evaluate number of eras with pieces"""
        eras_with_pieces = 0
        for era in [board.past, board.present, board.future]:
            if len(era.getPieces(self)) > 0:
                eras_with_pieces += 1
        return eras_with_pieces

    def _evaluate_focus(self, board: 'Board', next_era) -> int:
        """Evaluate pieces in focused era"""
        return len(next_era.getPieces(self))

    def _get_best_era(self, board: 'Board') -> 'Era':
        """Choose the best era to focus on next"""
        best_era = None
        best_score = -1
        
        for era in [board.past, board.present, board.future]:
            if era != self.current_era:  # Can't select current era
                pieces = len(era.getPieces(self))
                if pieces > best_score:
                    best_score = pieces
                    best_era = era
                elif pieces == best_score and random.random() < 0.5:
                    best_era = era
        
        # If no better option found, default to an era different from current
        if best_era is None:
            if self.current_era == board.past:
                best_era = board.present
            elif self.current_era == board.present:
                best_era = board.future
            else:
                best_era = board.past
                
        return best_era

    def _undo_move(self, board: 'Board', move: 'Move', original_pos: 'Position'):
        """Helper method to undo a simulated move"""
        if move.piece:
            # Restore piece to original position
            current_pos = move.piece.position
            current_era = current_pos._era
            current_era.grid[current_pos._y][current_pos._x].clearPiece()
            
            original_era = original_pos._era
            original_era.grid[original_pos._y][original_pos._x].setPiece(move.piece)

class RandomAIPlayer(PlayerStrategy):
    def getMove(self, board: 'Board') -> Move:
        """
        Randomly select a valid move from available moves
        """
        # Get pieces in current era
        pieces = self.current_era.getPieces(self)
        if not pieces:
            # If no pieces in current era, randomly select next era
            possible_eras = [board.past, board.present, board.future]
            possible_eras.remove(self.current_era)
            next_era = random.choice(possible_eras)
            return Move(None, [], next_era, 
                       "b_player" if self._color == "w_player" else "w_player")
        
        # Get all valid moves for each piece
        all_valid_moves = []
        for piece in pieces:
            piece_moves = board.get_moves_for_piece(piece)
            all_valid_moves.extend(piece_moves)
        
        if not all_valid_moves:
            # If no valid moves, randomly select next era
            possible_eras = [board.past, board.present, board.future]
            possible_eras.remove(self.current_era)
            next_era = random.choice(possible_eras)
            return Move(None, [], next_era, 
                       "b_player" if self._color == "w_player" else "w_player")
        
        # Select random move
        selected_move = random.choice(all_valid_moves)
        
        # Add random next era to the move
        possible_eras = [board.past, board.present, board.future]
        possible_eras.remove(self.current_era)
        next_era = random.choice(possible_eras)
        
        return Move(selected_move.piece, selected_move.directions, next_era,
                   "b_player" if self._color == "w_player" else "w_player")

class HumanPlayer(PlayerStrategy):
    def getMove(self, board: 'Board') -> Move:
        """Get move from human player input"""
        # Get valid moves for all pieces in current era
        valid_moves = {}
        max_directions = 1
        
        # Get pieces in current era
        pieces = self.current_era.getPieces(self)
        if not pieces:
            print("No copies to move")
            next_era = self._input_next_era(board)
            return Move(None, [], next_era, 
                       "b_player" if self._color == "w_player" else "w_player")
        
        # Get valid moves for each piece
        for piece in pieces:
            piece_moves = board.get_moves_for_piece(piece)
            if piece_moves:  # Only include pieces that can actually move
                valid_moves[piece] = piece_moves
                max_directions = max(max_directions, 
                                   max(len(move.directions) for move in piece_moves))
        
        # If no pieces can move
        if not valid_moves:
            print("No copies to move")
            next_era = self._input_next_era(board)
            return Move(None, [], next_era, 
                       "b_player" if self._color == "w_player" else "w_player")
        
        # Get piece selection from user
        piece = self._input_piece(board, valid_moves)
        if piece is None:
            return None
        
        # Special case: only one piece can move and it can only make one move
        if (len(valid_moves) == 1 and 
            len(valid_moves[piece]) == 1 and 
            len(valid_moves[piece][0].directions) == 1):
            directions = valid_moves[piece][0].directions
        else:
            directions = self._input_directions(board, piece, max_directions)
            if not directions:
                return None
        
        next_era = self._input_next_era(board)
        return Move(piece, directions, next_era, 
                   "b_player" if self._color == "w_player" else "w_player")

    def _input_piece(self, board: 'Board', valid_moves: dict) -> 'Piece':
        """Get valid piece selection from user."""
        while True:
            piece_id = input("Select a copy to move\n").strip().upper()
            
            # First check if piece exists in any era
            piece_found = False
            for piece in self.current_era.getPieces(self):
                if piece.id == piece_id:
                    piece_found = True
                    break
            
            # If piece wasn't found in current era, check other eras
            if not piece_found:
                for era in [board.past, board.present, board.future]:
                    if era != self.current_era:
                        for piece in era.getPieces(self):
                            if piece.id == piece_id and piece.owner == self._color:
                                print("Cannot select a copy from an inactive era")
                                piece_found = True
                                break
                    if piece_found:
                        break
                
                if not piece_found:
                    print("Not a valid copy")
                continue
            
            # Now check if the piece is in valid moves
            selected_piece = None
            for piece in valid_moves.keys():
                if piece.id == piece_id:
                    selected_piece = piece
                    break
            
            if not selected_piece:
                print("That copy cannot move")
                continue
            
            # Check if piece can make moves of maximum length
            max_move_length = max(len(move.directions) for moves in valid_moves.values() 
                                for move in moves)
            piece_max_length = max(len(move.directions) for move in valid_moves[selected_piece])
            
            if piece_max_length < max_move_length:
                print("That copy cannot move")
                continue
                
            return selected_piece

    def _input_directions(self, board: 'Board', piece: 'Piece', max_directions: int):
        """Select valid move directions."""
        valid_directions = {'n', 's', 'e', 'w', 'f', 'b'}
        directions = []
        
        # Get valid moves for this piece
        valid_moves = board.get_moves_for_piece(piece)
        
        # If piece can only make shorter moves than others, it can't be used
        if max(len(move.directions) for move in valid_moves) < max_directions:
            print("That copy cannot move")
            return None
            
        # Get first direction
        while True:
            direction = input("Select first direction to move ['n', 's', 'e', 'w', 'f', 'b']\n").strip().lower()
            if direction not in valid_directions:
                print("Not a valid direction")
                continue
                
            # Check if this is a valid first move
            temp_move = Move(piece, [direction], None, None)
            if not board.is_valid_direction(temp_move):
                print("Not a valid direction")
                continue
                
            directions.append(direction)
            break
        
        # If two moves are possible, get second direction
        if max_directions > 1:
            while True:
                direction = input("Select second direction to move ['n', 's', 'e', 'w', 'f', 'b']\n").strip().lower()
                if direction not in valid_directions:
                    print("Not a valid direction")
                    continue
                    
                # Check if complete move is valid
                temp_move = Move(piece, directions + [direction], None, None)
                if not board.is_valid_move(temp_move):
                    print("Invalid move")
                    continue
                    
                directions.append(direction)
                break
        
        return directions

    def _input_next_era(self, board: 'Board'):
        """Get valid next era selection."""
        valid_eras = {'past', 'present', 'future'}
        while True:
            era = input("Select the next era to focus on ['past', 'present', 'future']\n").strip().lower()

            if era not in valid_eras:
                print("Not a valid era")
                continue

            # Get the actual Era object instead of using the string
            next_era = getattr(board, era)  # This gets board.past, board.present, or board.future
            
            # Check if selected era is current era
            if next_era == self.current_era:
                print("Cannot select the current era")
                continue

            return next_era  # Return the Era object instead of the string