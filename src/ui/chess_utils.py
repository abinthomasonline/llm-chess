from typing import Optional

def get_chessboard_html(fen: Optional[str] = None, flip: bool = False) -> str:
    """Generate HTML for an interactive chessboard using chessboard.js"""
    
    # Default FEN for starting position if none provided
    fen = fen or "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    
    return f"""
        <div id="board-container" style="width: 600px; margin: auto;">
            <div id="board"></div>
        </div>
        
        <link
            rel="stylesheet"
            href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css"
            integrity="sha384-q94+BZtLrkL1/ohfjR8c6L+A6qzNH9R2hBLwyoAfu3i/WCvQjzL2RQJ3uNHDISdU"
            crossorigin="anonymous"
        />
        <script
            src="https://code.jquery.com/jquery-3.7.1.min.js"
            integrity="sha384-1H217gwSVyLSIfaLxHbE7dRb3v4mYCKbpQvzx0cegeju1MVsGrX5xXxAvs/HgeFs"
            crossorigin="anonymous"
        ></script>
        <script
            src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"
            integrity="sha384-8Vi8VHwn3vjQ9eUHUxex3JSN/NFqUg3QbPyX8kWyb93+8AC/pPWTzj+nHtbC5bxD"
            crossorigin="anonymous"
        ></script>
        
        <script>
            // Initialize the board with current position
            var board = Chessboard('board', {{
                position: '{fen}',
                orientation: '{("white", "black")[flip]}',
                showNotation: true,
                pieceTheme: 'https://lichess1.org/assets/piece/cburnett/{{piece}}.svg'
            }});
            
            // Make the board responsive
            $(window).resize(function() {{
                board.resize();
            }});
        </script>
        
        <style>
            #board-container {{
                padding: 20px;
                background: #f0f0f0;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
        </style>
    """

def get_move_history_html(moves: list[tuple[str, str, str]]) -> str:
    """Generate HTML for move history display"""
    
    html = """
        <div class="move-history">
            <table style="width: 100%;">
                <thead>
                    <tr>
                        <th>Move</th>
                        <th>White</th>
                        <th>Black</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    rows = []
    for i in range(0, len(moves), 2):
        move_num = i // 2 + 1
        white_move = f"{moves[i][1]}<br/><small>{moves[i][2]}</small>" if i < len(moves) else ""
        black_move = f"{moves[i+1][1]}<br/><small>{moves[i+1][2]}</small>" if i+1 < len(moves) else ""
        
        rows.append(f"""
            <tr>
                <td>{move_num}.</td>
                <td>{white_move}</td>
                <td>{black_move}</td>
            </tr>
        """)

    html += "".join(reversed(rows))
    
    html += """
                </tbody>
            </table>
        </div>
        
        <style>
            .move-history {
                margin: 20px;
                padding: 15px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }
            .move-history table {
                border-collapse: collapse;
            }
            .move-history th, .move-history td {
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #eee;
            }
            .move-history small {
                color: #666;
                font-size: 0.85em;
            }
        </style>
    """
    
    return html 