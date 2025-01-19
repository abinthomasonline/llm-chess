import chess
import chess.pgn
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Tuple

@dataclass
class GameState:
    """Represents the current state of a chess game"""
    board: chess.Board
    current_player: str
    move_history: List[Tuple[str, str, str]]  # List of (move, move_san, explanation) tuples
    game_result: Optional[str] = None
    start_time: datetime = datetime.now()

class ChessGame:
    """Manages a chess game state and operations"""
    
    def __init__(self, player1: str, player2: str):
        """Initialize a new chess game"""
        self.board = chess.Board()
        self.player1 = player1
        self.player2 = player2
        self.move_history: List[Tuple[str, str, str]] = []
        self.start_time = datetime.now()
        
    @property
    def current_player(self) -> str:
        """Get the current player's name"""
        return self.player1 if self.board.turn == chess.WHITE else self.player2
    
    @property
    def is_game_over(self) -> bool:
        """Check if the game is over"""
        return self.board.is_game_over()
    
    @property
    def result(self) -> str:
        """Get the game result"""
        if not self.is_game_over:
            return "*"
        if self.board.is_checkmate():
            return "1-0" if self.board.turn == chess.BLACK else "0-1"
        return "1/2-1/2"
    
    def get_legal_moves(self) -> List[str]:
        """Get list of legal moves in UCI format"""
        return [move.uci() for move in self.board.legal_moves]
    
    def make_move(self, move_uci: str, move_san: str, explanation: str = "") -> bool:
        """
        Make a move on the board
        
        Args:
            move_uci: Move in UCI format (e.g., "e2e4")
            move_san: Move in SAN format (e.g., "e4")
            explanation: Optional explanation of the move
            
        Returns:
            bool: True if move was successful
        """
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append((move_uci, move_san, explanation))
                return True
            return False
        except ValueError:
            return False
    
    def get_state(self) -> GameState:
        """Get current game state"""
        return GameState(
            board=self.board.copy(),
            current_player=self.current_player,
            move_history=self.move_history.copy(),
            game_result=self.result if self.is_game_over else None,
            start_time=self.start_time
        )
    
    def get_fen(self) -> str:
        """Get current position in FEN notation"""
        return self.board.fen()
    
    def export_pgn(self) -> str:
        """Export game in PGN format"""
        game = chess.pgn.Game()
        
        # Set headers
        game.headers["Event"] = "LLM Chess Battle"
        game.headers["Date"] = self.start_time.strftime("%Y.%m.%d")
        game.headers["White"] = self.player1
        game.headers["Black"] = self.player2
        game.headers["Result"] = self.result
        
        # Add moves
        node = game
        for move_uci, move_san, explanation in self.move_history:
            move = chess.Move.from_uci(move_uci)
            node = node.add_variation(move)
            if explanation:
                node.comment = explanation
        
        return str(game)
    
    def get_position_analysis(self) -> dict:
        """Get basic analysis of the current position"""
        return {
            "in_check": self.board.is_check(),
            "in_checkmate": self.board.is_checkmate(),
            "in_stalemate": self.board.is_stalemate(),
            "is_insufficient_material": self.board.is_insufficient_material(),
            "is_fifty_moves": self.board.is_fifty_moves(),
            "is_repetition": self.board.is_repetition(),
            "fullmove_number": self.board.fullmove_number,
            "piece_count": {
                "white": len(self.board.pieces(chess.PAWN, chess.WHITE)) +
                        len(self.board.pieces(chess.KNIGHT, chess.WHITE)) +
                        len(self.board.pieces(chess.BISHOP, chess.WHITE)) +
                        len(self.board.pieces(chess.ROOK, chess.WHITE)) +
                        len(self.board.pieces(chess.QUEEN, chess.WHITE)),
                "black": len(self.board.pieces(chess.PAWN, chess.BLACK)) +
                        len(self.board.pieces(chess.KNIGHT, chess.BLACK)) +
                        len(self.board.pieces(chess.BISHOP, chess.BLACK)) +
                        len(self.board.pieces(chess.ROOK, chess.BLACK)) +
                        len(self.board.pieces(chess.QUEEN, chess.BLACK))
            }
        }
