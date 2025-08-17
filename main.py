from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from analyzer import analyze_pgn
from engine import EnginePool

app = FastAPI(title="Chess Analysis API", version="0.1.0")

class AnalyzeRequest(BaseModel):
    pgn: str = Field(..., description="Full PGN of the game to analyze")
    depth: int = Field(18, ge=6, le=40)
    multipv: int = Field(3, ge=1, le=5)

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    try:
        report = analyze_pgn(req.pgn, depth=req.depth, multipv=req.multipv)
        return {"ok": True, "report": report}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.on_event("shutdown")
def shutdown_event():
    EnginePool.close()
