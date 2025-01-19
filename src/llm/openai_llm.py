import json
from typing import Optional
import openai
import time
from src.llm.base import BaseLLM, ChessMove

class OpenAILLM(BaseLLM):
    """OpenAI GPT implementation of the LLM interface"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo", temperature: float = 0.7):
        super().__init__(api_key, temperature)
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    async def get_next_move(self, 
                           board_fen: str, 
                           move_history: list[str],
                           legal_moves: list[str]) -> ChessMove:
        """Get next move using OpenAI's API"""
        print("Calling OpenAI API")
        self._rate_limit()
        
        prompt = self._get_chess_prompt(board_fen, move_history, legal_moves)
        start_time = time.time()

        for i in range(1, self.retries + 1):
        
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a skilled chess engine."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    response_format={"type": "json_object"}
                )

                
                thinking_time = time.time() - start_time
                
                try:
                    result = json.loads(response.choices[0].message.content)
                    if result["move"] not in legal_moves and i < self.retries:
                        print(f"Move {result['move']} not in legal moves {legal_moves}, retrying...")
                        continue
                    print("Returning move from OpenAI, ", result["move"])
                    return ChessMove(
                        move=result["move"],
                        explanation=result["explanation"],
                        confidence=float(result["confidence"]),
                        thinking_time=thinking_time
                    )
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Invalid response format from OpenAI: {e}")
                    raise ValueError(f"Invalid response format from OpenAI: {e}")
                    
            except Exception as e:
                print(f"Error calling OpenAI API: {str(e)}")
                raise Exception(f"Error calling OpenAI API: {str(e)}") 