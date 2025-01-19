import sys
from pathlib import Path
import asyncio
import os
from dotenv import load_dotenv

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.llm.openai_llm import OpenAILLM
from src.llm.anthropic_llm import AnthropicLLM
from src.controller.game_controller import GameController

async def test_game_controller():
    """Test the game controller with a short game"""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize LLMs
    openai_llm = OpenAILLM(api_key=os.getenv("OPENAI_API_KEY"))
    anthropic_llm = AnthropicLLM(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Create game controller with 5-minute time control
    controller = GameController(
        white_player=openai_llm,
        black_player=anthropic_llm,
        time_control=300,  # 5 minutes per player
        max_moves=10  # Limit to 10 moves for testing
    )
    
    print("\nStarting test game between OpenAI and Anthropic...")
    
    # Play the game
    pgn = await controller.play_game()
    
    print("\nGame completed!")
    print("\nFinal PGN with statistics:")
    print(pgn)
    
    # Basic assertions
    assert controller.game_stats["total_moves"] > 0
    assert controller.game_stats["average_time_per_move"]["white"] > 0
    assert controller.game_stats["average_time_per_move"]["black"] > 0
    assert "Game Statistics:" in pgn
    
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    asyncio.run(test_game_controller()) 