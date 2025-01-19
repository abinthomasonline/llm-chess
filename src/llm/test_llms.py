import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.llm.openai_llm import OpenAILLM
from src.llm.anthropic_llm import AnthropicLLM

async def test_llm(llm, name: str):
    """Test an LLM implementation with a simple chess position"""
    
    # Starting position FEN
    initial_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    
    print(f"\nTesting {name}...")
    try:
        move = await llm.get_next_move(
            board_fen=initial_fen,
            move_history=[],
            time_remaining=300
        )
        print(f"Move: {move.move}")
        print(f"Explanation: {move.explanation}")
        print(f"Confidence: {move.confidence}")
        print(f"Thinking time: {move.thinking_time:.2f}s")
        print("Test successful!")
    except Exception as e:
        print(f"Error testing {name}: {str(e)}")

async def main():
    # Load environment variables
    load_dotenv()
    
    # Get API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_key or not anthropic_key:
        print("Please set OPENAI_API_KEY and ANTHROPIC_API_KEY in your .env file")
        return
    
    # Initialize LLMs
    openai_llm = OpenAILLM(api_key=openai_key)
    anthropic_llm = AnthropicLLM(api_key=anthropic_key)
    
    # Test both LLMs
    await test_llm(openai_llm, "OpenAI GPT-4")
    await test_llm(anthropic_llm, "Anthropic Claude")

if __name__ == "__main__":
    asyncio.run(main()) 