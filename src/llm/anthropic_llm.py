import json
from typing import Optional
from anthropic import Anthropic
import time
from src.llm.base import BaseLLM, ChessMove

class AnthropicLLM(BaseLLM):
    """Anthropic Claude implementation of the LLM interface"""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229", temperature: float = 0.7):
        super().__init__(api_key, temperature)
        self.client = Anthropic(api_key=api_key)
        self.model = model

    async def get_next_move(self, 
                           board_fen: str, 
                           move_history: list[str],
                           legal_moves: list[str]) -> ChessMove:
        """Get next move using Anthropic's API"""
        print("Calling Anthropic API")
        self._rate_limit()
        
        prompt = self._get_chess_prompt(board_fen, move_history, legal_moves)
        start_time = time.time()

        for i in range(1, self.retries + 1):
        
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=self.temperature,
                    system="You are a skilled chess engine. Respond only with JSON.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                
                thinking_time = time.time() - start_time
                
                try:
                    result = json.loads(response.content[0].text)
                    if result["move"] not in legal_moves and i < self.retries:
                        print(f"Move {result['move']} not in legal moves {legal_moves}, retrying...")
                        continue
                    print("Returning move from Anthropic, ", result["move"])
                    return ChessMove(
                        move=result["move"],
                        explanation=result["explanation"],
                        confidence=float(result["confidence"]),
                        thinking_time=thinking_time
                    )
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Invalid response format from Anthropic: {e}")
                    raise ValueError(f"Invalid response format from Anthropic: {e}")
                    
            except Exception as e:
                print(f"Error calling Anthropic API: {str(e)}")
                raise Exception(f"Error calling Anthropic API: {str(e)}") 