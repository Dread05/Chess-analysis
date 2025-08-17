# Chess Analysis Engine (Portable for Render.com)

## Setup
1. Download Stockfish binary for Linux from https://stockfishchess.org/download/
2. Place the `stockfish` executable in the root of this folder (next to engine.py).
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

Then open http://localhost:8000/docs to test.
