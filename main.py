from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from analyzer import analyze_pgn
from engine import EnginePool
from fastapi.responses import HTMLResponse

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

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
      <head>
        <title>Chess Analysis</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 40px; }
          textarea { width: 100%; height: 200px; font-family: monospace; }
          button { padding: 10px 20px; margin-top: 10px; cursor: pointer; }
          pre { background: #f4f4f4; padding: 10px; white-space: pre-wrap; }
        </style>
      </head>
      <body>
        <h1>Chess Analysis</h1>
        <p>Paste a PGN and click Analyze:</p>
        <textarea id="pgn"></textarea><br>
        <button onclick="analyze()">Analyze</button>
        <h2>Results</h2>
        <pre id="result"></pre>

        <script>
          async function analyze() {
            const pgn = document.getElementById("pgn").value;
            if (!pgn.trim()) {
              alert("Please paste a PGN first!");
              return;
            }
            document.getElementById("result").textContent = "Analyzing...";
            try {
              const res = await fetch("/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ pgn: pgn, depth: 12, multipv: 2 })
              });
              const data = await res.json();
              document.getElementById("result").textContent =
                JSON.stringify(data, null, 2);
            } catch (err) {
              document.getElementById("result").textContent =
                "Error: " + err;
            }
          }
        </script>
      </body>
    </html>
    """
