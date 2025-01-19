from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import time
from dataclasses import dataclass

@dataclass
class ChessMove:
    """Represents a chess move with explanation"""
    move: str
    explanation: str
    confidence: float
    thinking_time: float

class BaseLLM(ABC):
    """Abstract base class for LLM interactions"""
    
    def __init__(self, api_key: str, temperature: float = 0.7):
        self.api_key = api_key
        self.temperature = temperature
        self.last_call_time = 0
        self.min_delay = 1.0  # Minimum delay between API calls in seconds
        self.retries = 3

    def _rate_limit(self):
        """Implement basic rate limiting"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        if time_since_last_call < self.min_delay:
            time.sleep(self.min_delay - time_since_last_call)
        self.last_call_time = time.time()

    @abstractmethod
    async def get_next_move(self, 
                           board_fen: str, 
                           move_history: list[str],
                           legal_moves: list[str]) -> ChessMove:
        """
        Get the next chess move from the LLM.
        
        Args:
            board_fen: Current board position in FEN notation
            move_history: List of previous moves in algebraic notation
            legal_moves: List of legal moves in san format
        Returns:
            ChessMove object containing the move and explanation
        """
        pass

    def _get_chess_prompt(self, 
                         board_fen: str, 
                         move_history: list[str],
                         legal_moves: list[str]) -> str:
        """Generate the chess prompt for the LLM"""
        prompt = (
            "You are playing a game of chess. Analyze the position and make the best move.\n\n"
            f"Current position (FEN): {board_fen}\n"
        )
        
        if move_history:
            prompt += "\nPrevious moves:\n"
            for i, move in enumerate(move_history, 1):
                prompt += f"{i}. {move}\n"

        prompt += "\nLegal moves:\n"
        prompt += ", ".join(legal_moves)
            
        prompt += "\n\nRespond with your move in algebraic notation (e.g., 'e4', 'Nf3', etc.)"
        prompt += "\nand a brief explanation of your thinking."
        prompt += "\nFormat your response as JSON with keys: 'move', 'explanation', 'confidence' (0-1)"
        
        return prompt
