import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import asyncio
from typing import Optional

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.llm.openai_llm import OpenAILLM
from src.llm.anthropic_llm import AnthropicLLM
from src.controller.game_controller import GameController
from src.chess_engine.game import ChessGame
from src.ui.chess_utils import get_chessboard_html, get_move_history_html

# Load environment variables
load_dotenv()

def initialize_session_state():
    """Initialize session state variables"""
    if 'game_controller' not in st.session_state:
        st.session_state.game_controller = None
    if 'current_game' not in st.session_state:
        st.session_state.current_game = None
    if 'game_in_progress' not in st.session_state:
        st.session_state.game_in_progress = False
    if 'last_move_count' not in st.session_state:
        st.session_state.last_move_count = 0
    if 'game_finished' not in st.session_state:
        st.session_state.game_finished = False
    if 'pgn' not in st.session_state:
        st.session_state.pgn = None

def create_game_controller(white_player: str, black_player: str, 
                         time_control: Optional[int], max_moves: Optional[int]) -> GameController:
    """Create a new game controller with specified players"""
    
    # Initialize LLMs
    players = {
        'OpenAI': lambda: OpenAILLM(api_key=os.getenv("OPENAI_API_KEY")),
        'Anthropic': lambda: AnthropicLLM(api_key=os.getenv("ANTHROPIC_API_KEY"))
    }
    
    white = players[white_player]()
    black = players[black_player]()
    
    return GameController(
        white_player=white,
        black_player=black,
        time_control=time_control,
        max_moves=max_moves
    )

def display_game_board():
    """Display the current game state"""
    if st.session_state.current_game:
        # Display chessboard
        st.components.v1.html(
            get_chessboard_html(
                fen=st.session_state.current_game.get_fen(),
                flip=False
            ),
            height=650
        )
        
        # Display move history
        if st.session_state.current_game.move_history:
            st.components.v1.html(
                get_move_history_html(st.session_state.current_game.move_history),
                height=400, 
                scrolling=True
            )

async def play_single_move():
    """Play a single move in the game"""
    if st.session_state.game_controller and not st.session_state.game_finished:
        try:
            # Get current player
            current_player = st.session_state.game_controller._get_current_player()
            color = "white" if st.session_state.game_controller.game.board.turn else "black"

            # Check for game end conditions
            if st.session_state.game_controller.game.is_game_over:
                st.session_state.game_finished = True
                st.session_state.pgn = st.session_state.game_controller.export_game()
                return False
            
            # Get and validate move
            move = await st.session_state.game_controller._get_next_move(current_player, color)
            if move:
                st.session_state.last_move_count = len(st.session_state.current_game.move_history)
                return True
            else:
                st.session_state.game_finished = True
                st.session_state.pgn = st.session_state.game_controller.export_game()
                return False
                
        except Exception as e:
            st.error(f"Error during move: {str(e)}")
            st.session_state.game_finished = True
            return False

def main():
    st.set_page_config(page_title="LLM Chess Battle", layout="wide")
    initialize_session_state()
    
    st.title("LLM Chess Battle")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Game Configuration")
        
        white_player = st.selectbox(
            "White Player",
            options=['OpenAI', 'Anthropic'],
            key='white_player'
        )
        
        black_player = st.selectbox(
            "Black Player",
            options=['Anthropic', 'OpenAI'],
            key='black_player'
        )
        
        time_control = st.number_input(
            "Time Control (seconds)",
            min_value=30,
            max_value=3600,
            value=300,
            step=30
        )
        
        max_moves = st.number_input(
            "Maximum Moves",
            min_value=10,
            max_value=200,
            value=50,
            step=10
        )
        
        if st.button("Start New Game"):
            st.session_state.game_controller = create_game_controller(
                white_player, black_player, time_control, max_moves
            )
            st.session_state.current_game = st.session_state.game_controller.game
            st.session_state.game_in_progress = True
            st.session_state.game_finished = False
            st.session_state.last_move_count = 0
            st.session_state.pgn = None
    
    # Main content area
    if not st.session_state.current_game:
        st.info("Configure and start a new game using the sidebar controls.")
    else:
        # Display the game board and move history
        display_game_board()
        
        # Game controls
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.game_in_progress and not st.session_state.game_finished:
                if st.button("Stop Game"):
                    st.session_state.game_in_progress = False
            elif not st.session_state.game_finished:
                if st.button("Continue Game"):
                    st.session_state.game_in_progress = True
        
        with col2:
            if st.button("Reset Game"):
                st.session_state.game_controller = None
                st.session_state.current_game = None
                st.session_state.game_in_progress = False
                st.session_state.game_finished = False
                st.session_state.last_move_count = 0
                st.session_state.pgn = None
                st.rerun()

        # Run the game
        if st.session_state.game_in_progress and not st.session_state.game_finished:
            # Create a placeholder for the progress message
            status_placeholder = st.empty()
            
            # Play a single move
            with status_placeholder:
                with st.spinner('Thinking...'):
                    move_made = asyncio.run(play_single_move())
                    
                    if move_made:
                        st.rerun()
                    else:
                        st.session_state.game_finished = True

        print("st.session_state.pgn", st.session_state.pgn)
        print("st.session_state.game_finished", st.session_state.game_finished)
        
        # Display final PGN when game is finished
        if st.session_state.game_finished and st.session_state.pgn:
            st.text_area("Game PGN", st.session_state.pgn, height=300)

if __name__ == "__main__":
    main() 