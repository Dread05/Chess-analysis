import os
import chess
import chess.engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Always use bundled stockfish binary inside project folder
STOCKFISH_PATH = os.path.join(BASE_DIR, "stockfish")

MAX_DEPTH = int(os.getenv("MAX_DEPTH", "18"))
DEFAULT_MULTIPV = int(os.getenv("MULTIPV", "3"))

class EnginePool:
    _engine = None

    @classmethod
    def get(cls):
        if cls._engine is None:
            cls._engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
            cls._engine.configure({
                "Threads": max(1, os.cpu_count()//2),
                "Hash": 256,
                "MultiPV": DEFAULT_MULTIPV
            })
        return cls._engine

    @classmethod
    def close(cls):
        if cls._engine:
            try:
                cls._engine.quit()
            finally:
                cls._engine = None


def analyze_position(board: chess.Board, depth: int = MAX_DEPTH, multipv: int = DEFAULT_MULTIPV):
    eng = EnginePool.get()
    eng.configure({"MultiPV": multipv})
    info = eng.analyse(board, chess.engine.Limit(depth=depth), multipv=multipv)
    if isinstance(info, dict):
        info = [info]

    lines = []
    for i, item in enumerate(info, start=1):
        move = item.get("pv", [None])[0]
        score = item.get("score")
        if score.is_mate():
            val = {"type": "mate", "value": score.white().mate()}
        else:
            val = {"type": "cp", "value": score.white().score(mate_score=100000)}
        lines.append({
            "rank": i,
            "best_move_uci": move.uci() if move else None,
            "score": val,
            "pv": [m.uci() for m in item.get("pv", [])]
        })
    return lines
