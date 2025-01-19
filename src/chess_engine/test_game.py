import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.chess_engine.game import ChessGame

def test_chess_game():
    """Test basic chess game functionality"""
    
    # Initialize game
    game = ChessGame("Player1", "Player2")
    
    # Test initial state
    print("\nTesting initial state...")
    assert not game.is_game_over
    assert game.result == "*"
    assert game.current_player == "Player1"
    assert game.get_fen().startswith("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    print("Initial state OK!")
    
    # Test making moves
    print("\nTesting moves...")
    assert game.make_move("e2e4", "e4", "King's pawn opening")
    assert game.make_move("e7e5", "e5", "King's pawn response")
    assert len(game.move_history) == 2
    print("Moves OK!")
    
    # Test position analysis
    print("\nTesting position analysis...")
    analysis = game.get_position_analysis()
    assert not analysis["in_check"]
    assert not analysis["in_checkmate"]
    assert analysis["piece_count"]["white"] == analysis["piece_count"]["black"]
    print("Position analysis OK!")
    
    # Test PGN export
    print("\nTesting PGN export...")
    pgn = game.export_pgn()
    assert "1. e4" in pgn
    assert "1... e5" in pgn
    assert "King's pawn opening" in pgn
    print("PGN export OK!")
    
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    test_chess_game() 