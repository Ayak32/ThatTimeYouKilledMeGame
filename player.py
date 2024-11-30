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
        self._activated_pieces = []  # Track pieces activated from supply
        self._deactivated_pieces = []  # Track pieces that were deactivated
        
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
            self._supply = [
                Piece("D", color, None),
                Piece("E", color, None),
                Piece("F", color, None),
                Piece("G", color, None)]
 

    def activate_piece(self, piece_id: str):
        """Move a piece from supply to active pieces"""
        for piece in self._supply:
            if piece.id == piece_id:
                self._supply.remove(piece)
                self._pieces.append(piece)
                self._activated_pieces.append(piece)
                return piece
        return None

    def deactivate_piece(self, piece: Piece):
        """Move a piece back to supply"""
        if piece in self._pieces:
            self._pieces.remove(piece)
            self._supply.append(piece)
            if piece in self._activated_pieces:
                self._activated_pieces.remove(piece)
            self._deactivated_pieces.append(piece)
    
    @abstractmethod
    def getMove(self, board: Board) -> Move:
        pass

class HeuristicAIPlayer(PlayerStrategy):
    def getMove(self, board: 'Board') -> Move:
        """Get the best move based on heuristic evaluation"""
        valid_moves = board.getValidMoves(self)
        
        # Display current scores if score display is enabled
        if board.score:
            self._display_scores(board)
        
        # If no valid moves in current era, find an era where we CAN make moves
        if not valid_moves:
            # First, try to find eras where we have pieces AND can make moves
            best_era = None
            best_era_score = float('-inf')
            
            for era in [board.past, board.present, board.future]:
                if era != self.current_era:
                    # Temporarily switch era to check for valid moves
                    original_era = self.current_era
                    self.current_era = era
                    possible_moves = board.getValidMoves(self)
                    self.current_era = original_era
                    
                    if possible_moves:  # If we can make moves in this era
                        # Score this era based on our heuristics
                        era_score = (
                            3 * len(era.getPieces(self)) +  # Prefer eras with more of our pieces
                            2 * (len(era.getPieces(self)) - len(era.getPieces(board.b_player if self == board.w_player else board.w_player))) +  # Piece advantage
                            1 * (2 if era == board.present else 1)  # Slight preference for present era
                        )
                        
                        if era_score > best_era_score:
                            best_era_score = era_score
                            best_era = era
            
            # If we found an era where we can make moves, go there
            if best_era:
                return Move(None, [], best_era, self._color)
            
            # If we can't make moves anywhere, choose based on piece presence
            eras_with_pieces = [era for era in [board.past, board.present, board.future]
                               if era != self.current_era and len(era.getPieces(self)) > 0]
            
            if eras_with_pieces:
                next_era = max(eras_with_pieces, key=lambda era: len(era.getPieces(self)))
            else:
                # If no pieces in other eras, choose present era
                next_era = board.present if self.current_era != board.present else board.past
            
            return Move(None, [], next_era, self._color)
        
        # We have valid moves, evaluate each one
        best_move = None
        best_score = float('-inf')
        
        for move in valid_moves:
            # Ensure move has a next era selected
            if move.next_era is None:
                # Temporarily try each possible next era to find the best one
                best_next_era = None
                best_next_score = float('-inf')
                
                for possible_era in [board.past, board.present, board.future]:
                    if possible_era != self.current_era:
                        move.next_era = possible_era
                        # Simulate move
                        original_pos = move.piece.position if move.piece else None
                        success = move.execute(board)
                        
                        if success:
                            next_score = (
                                3 * self._evaluate_era_presence(board) +
                                2 * self._evaluate_piece_advantage(board, self) +
                                1 * len(self._supply) +
                                1 * self._evaluate_centrality(board, self) +
                                1 * self._evaluate_focus(board, possible_era)
                            )
                            
                            # Undo move simulation
                            self._undo_move(board, move, original_pos)
                            
                            if next_score > best_next_score:
                                best_next_score = next_score
                                best_next_era = possible_era
                
                move.next_era = best_next_era
            
            # Now evaluate the complete move
            original_pos = move.piece.position if move.piece else None
            success = move.execute(board)
            
            if success:
                era_presence = self._evaluate_era_presence(board)
                
                # Check for winning move
                if self._count_opponent_eras(board) <= 1:
                    score = 9999
                else:
                    score = (
                        3 * era_presence +
                        2 * self._evaluate_piece_advantage(board, self) +
                        1 * len(self._supply) +
                        1 * self._evaluate_centrality(board, self) +
                        1 * self._evaluate_focus(board, move.next_era)
                    )
                
                # Undo move simulation
                self._undo_move(board, move, original_pos)
                
                # Update best move if score is higher
                if score > best_score:
                    best_score = score
                    best_move = move
                elif score == best_score and random.random() < 0.5:
                    best_move = move
        
        return best_move

    def _display_scores(self, board):
        """Display unweighted scores for both players"""
        for player, color in [(board.w_player, "white"), (board.b_player, "black")]:
            era_presence = self._evaluate_era_presence(board)
            piece_advantage = self._evaluate_piece_advantage(board, player)
            supply = len(player._supply)
            centrality = self._evaluate_centrality(board, player)
            focus = self._evaluate_focus(board, player.current_era)
            
            print(f"{color}'s score: {era_presence} eras, {piece_advantage} advantage, "
                  f"{supply} supply, {centrality} centrality, {focus} in focus")

    def _count_eras_with_pieces(self, board: 'Board', player: 'PlayerStrategy') -> int:
        """Count number of eras containing player's pieces"""
        count = 0
        for era in [board.past, board.present, board.future]:
            if len(era.getPieces(player)) > 0:
                count += 1
        return count

    @staticmethod
    def _evaluate_piece_advantage(board: 'Board', player: 'PlayerStrategy') -> int:
        """Calculate piece advantage across all eras"""
        advantage = 0
        
        # Use color for comparison to determine opponent
        opponent = board.b_player if player._color == "w_player" else board.w_player
        
        # Calculate advantage across all eras
        for era in [board.past, board.present, board.future]:
            # Get pieces for current player in this era
            player_pieces = len([piece for piece in era.getPieces(player) if piece.owner == player._color])
            
            # Get pieces for opponent in this era
            opponent_pieces = len([piece for piece in era.getPieces(opponent) if piece.owner == opponent._color])
            
            # Add difference to total advantage
            advantage += player_pieces - opponent_pieces
        
        return advantage

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

    def _count_opponent_eras(self, board):
        """Count number of eras containing opponent's pieces"""
        opponent = board.b_player if self == board.w_player else board.w_player
        count = 0
        for era in [board.past, board.present, board.future]:
            if len(era.getPieces(opponent)) > 0:
                count += 1
        return count

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
            
            # 1. Check if piece exists on the board at all
            piece_found = False
            for era in [board.past, board.present, board.future]:
                for piece in era.getPieces(None):  # Get all pieces regardless of owner
                    if piece.id == piece_id:
                        piece_found = True
                        # 2. Check if it's an opponent's piece
                        if piece.owner != self._color:
                            print("That is not your copy")
                            break
                        # 3. Check if piece is in inactive era
                        if era != self.current_era:
                            print("Cannot select a copy from an inactive era")
                            break
                        # If we get here, it's a valid piece in the active era
                        return piece
                if piece_found:
                    break
            
            if not piece_found:
                print("Not a valid copy")

    def _input_directions(self, board: 'Board', piece: 'Piece', max_directions: int):
        """Select valid move directions."""
        valid_directions = {'n', 's', 'e', 'w', 'f', 'b'}
        directions = []
        
        # Get first direction
        while True:
            direction = input("Select the first direction to move ['n', 'e', 's', 'w', 'f', 'b']\n").strip().lower()
            
            # 4. Check if direction is valid
            if direction not in valid_directions:
                print("Not a valid direction")
                continue
            
            # 5. Check if piece can move in that direction
            temp_move = Move(piece, [direction], None, None)
            if not board.is_valid_direction(temp_move):
                print(f"Cannot move {direction}")
                continue
            
            directions.append(direction)
            break

        # Similar checks for second direction if needed
        if max_directions > 1:
            while True:
                direction = input("Select the second direction to move ['n', 'e', 's', 'w', 'f', 'b']\n").strip().lower()
                if direction not in valid_directions:
                    print("Not a valid direction")
                    continue
                
                temp_move = Move(piece, directions + [direction], None, None)
                if not board.is_valid_move(temp_move):
                    print(f"Cannot move {direction}")
                    continue
                
                directions.append(direction)
                break
        
        return directions

    def _input_next_era(self, board: 'Board'):
        """Get valid next era selection."""
        valid_eras = {'past', 'present', 'future'}
        while True:
            era = input("Select the next era to focus on ['past', 'present', 'future']\n").strip().lower()

            # 6. Check if era is valid
            if era not in valid_eras:
                print("Not a valid era")
                continue

            next_era = getattr(board, era)
            
            # 7. Check if era is current era
            if next_era == self.current_era:
                print("Cannot select the current era")
                continue

            return next_era