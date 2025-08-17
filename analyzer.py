import io
import chess
import chess.pgn
from typing import List, Dict, Any, Optional
from engine import analyze_position

INACCURACY = 50
MISTAKE = 100
BLUNDER = 300

def score_to_cp(score_obj: Dict[str, int]) -> Optional[int]:
    if score_obj["type"] == "cp":
        return score_obj["value"]
    if score_obj["type"] == "mate":
        m = score_obj["value"]
        if m is None:
            return None
        return 100000 if m > 0 else -100000
    return None

def classify(cpl: int) -> str:
    abs_cpl = abs(cpl)
    if abs_cpl >= BLUNDER:
        return "blunder"
    if abs_cpl >= MISTAKE:
        return "mistake"
    if abs_cpl >= INACCURACY:
        return "inaccuracy"
    return "good"

def analyze_pgn(pgn_text: str, depth: int = 18, multipv: int = 3) -> Dict[str, Any]:
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    if game is None:
        raise ValueError("Invalid PGN")
    board = game.board()
    moves = list(game.mainline_moves())

    results: List[Dict[str, Any]] = []
    move_number = 1

    for ply, move in enumerate(moves, start=1):
        lines_before = analyze_position(board, depth=depth, multipv=multipv)
        best_before = lines_before[0]["score"]
        best_before_cp = score_to_cp(best_before) or 0

        board.push(move)

        lines_after = analyze_position(board, depth=depth, multipv=multipv)
        best_after = lines_after[0]["score"]
        best_after_cp = score_to_cp(best_after) or 0

        mover_is_white = (ply % 2 == 1)
        signed_before = best_before_cp if mover_is_white else -best_before_cp
        signed_after  = best_after_cp  if mover_is_white else -best_after_cp
        cpl = signed_before - signed_after

        tag = classify(cpl)
        san = board.peek().san()

        results.append({
            "ply": ply,
            "move_number": move_number if mover_is_white else move_number - 1,
            "side": "White" if mover_is_white else "Black",
            "move_uci": move.uci(),
            "move_san": san,
            "score_before": best_before,
            "score_after": best_after,
            "centipawn_loss": cpl,
            "tag": tag,
            "multipv_before": lines_before,
            "multipv_after": lines_after
        })
        if not mover_is_white:
            move_number += 1

    return {
        "event": game.headers.get("Event", ""),
        "white": game.headers.get("White", ""),
        "black": game.headers.get("Black", ""),
        "result": game.headers.get("Result", ""),
        "depth": depth,
        "multipv": multipv,
        "moves": results
    }
