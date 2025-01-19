import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from src.chess_engine.game import ChessGame
from src.llm.base import BaseLLM, ChessMove

class GameController:
    """Controls a chess match between two LLMs"""
    
    def __init__(
        self,
        white_player: BaseLLM,
        black_player: BaseLLM,
        time_control: Optional[int] = None,  # Time per player in seconds
        max_moves: Optional[int] = None  # Maximum number of moves before draw
    ):
        self.white_player = white_player
        self.black_player = black_player
        self.time_control = time_control
        self.max_moves = max_moves
        
        # Initialize game state
        self.game = ChessGame(
            player1=f"LLM-White ({type(white_player).__name__})",
            player2=f"LLM-Black ({type(black_player).__name__})"
        )
        
        # Time management
        self.time_remaining = {
            "white": time_control,
            "black": time_control
        } if time_control else None
        
        self.move_times: Dict[str, float] = {
            "white": [],
            "black": []
        }
        
        self.start_time = None
        self.game_stats = {
            "total_moves": 0,
            "average_time_per_move": {"white": 0.0, "black": 0.0},
            "longest_think_time": {"white": 0.0, "black": 0.0}
        }

    async def play_game(self) -> str:
        """
        Play a complete game between the two LLMs
        
        Returns:
            str: Game PGN with result
        """
        self.start_time = datetime.now()
        
        try:
            while not self._is_game_finished():
                # Get current player
                current_player = self._get_current_player()
                color = "white" if self.game.board.turn else "black"
                
                # Get and validate move
                move = await self._get_next_move(current_player, color)
                if not move:
                    # If no valid move, current player loses
                    self.game_stats["result"] = "0-1" if color == "white" else "1-0"
                    self.game_stats["termination"] = f"Invalid move by {color}"
                    break
                
                # Update statistics
                self._update_stats(move, color)
                
            return self.export_game()
            
        except Exception as e:
            # Log the error and end the game
            self.game_stats["termination"] = f"Error: {str(e)}"
            return self.export_game()

    async def _get_next_move(self, player: BaseLLM, color: str) -> Optional[bool]:
        """Get and validate the next move from an LLM"""
        try:
            # Calculate time remaining
            time_remaining = (
                self.time_remaining[color] if self.time_remaining else None
            )

            legal_moves = [self.game.board.san(move) for move in self.game.board.legal_moves]
            
            # Get move from LLM
            move_result = await player.get_next_move(
                board_fen=self.game.get_fen(),
                move_history=[move for _, move, _ in self.game.move_history], 
                legal_moves=legal_moves
            )
            
            # Update time remaining if using time control
            if self.time_remaining:
                self.time_remaining[color] -= move_result.thinking_time
                if self.time_remaining[color] <= 0:
                    self.game_stats["termination"] = f"{color} lost on time"
                    return None
                
            # Convert algebraic notation to UCI format
            try:
                san_move = move_result.move
                uci_move = self.game.board.parse_san(san_move).uci()
                move_result.move = uci_move
            except ValueError:
                print(f"Invalid move format from {color} player: {move_result.move}")
                return None
            
            # Make the move
            success = self.game.make_move(
                move_result.move,
                san_move,
                f"{move_result.explanation} (confidence: {move_result.confidence:.2f})"
            )
            
            return move_result if success else success
            
        except Exception as e:
            print(f"Error getting move from {color} player: {str(e)}")
            return None

    def _get_current_player(self) -> BaseLLM:
        """Get the current player based on board state"""
        return self.white_player if self.game.board.turn else self.black_player

    def _is_game_finished(self) -> bool:
        """Check if the game is finished"""
        # Check normal chess endings
        if self.game.is_game_over:
            self.game_stats["termination"] = "Normal chess ending"
            self.game_stats["result"] = self.game.result()
            return True
            
        # Check max moves
        if self.max_moves and self.game_stats["total_moves"] >= self.max_moves:
            self.game_stats["termination"] = "Maximum moves reached"
            return True
            
        return False

    def _update_stats(self, move: ChessMove, color: str):
        """Update game statistics after a move"""
        self.game_stats["total_moves"] += 1
        self.move_times[color].append(move.thinking_time)
        
        # Update average time
        self.game_stats["average_time_per_move"][color] = (
            sum(self.move_times[color]) / len(self.move_times[color])
        )
        
        # Update longest think time
        if move.thinking_time > self.game_stats["longest_think_time"][color]:
            self.game_stats["longest_think_time"][color] = move.thinking_time

    def export_game(self) -> str:
        """Export the game with metadata"""
        print("Exporting game")
        pgn = self.game.export_pgn()
        
        # Add game statistics as comments
        stats_comment = (
            f"Game Statistics:\n"
            f"Total Moves: {self.game_stats['total_moves']}\n"
            f"Average Think Time - White: {self.game_stats['average_time_per_move']['white']:.2f}s, "
            f"Black: {self.game_stats['average_time_per_move']['black']:.2f}s\n"
            f"Longest Think Time - White: {self.game_stats['longest_think_time']['white']:.2f}s, "
            f"Black: {self.game_stats['longest_think_time']['black']:.2f}s\n"
        )
        
        if "termination" in self.game_stats:
            stats_comment += f"Termination: {self.game_stats['termination']}\n"

        if self.game_stats["result"] != "*":
            stats_comment += f"Result: {self.game_stats['result']}\n"

        print("stats_comment", stats_comment)
        return f"{pgn}\n\n{stats_comment}"
