from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from engine import engine
import io

app = FastAPI(title="TF-IDF Document Search Engine API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchResponse(BaseModel):
    filename: str
    score: float
    snippet: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(('.txt', '.pdf')):
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported")
    
    content = await file.read()
    file_stream = io.BytesIO(content)
    
    success, message = engine.add_document(filename=file.filename, file_stream=file_stream)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
        
    return {"message": message}

@app.get("/search", response_model=List[SearchResponse])
async def search(q: str):
    if not q.strip():
        return []
        
    results = engine.search(q)
    return results

@app.get("/stats")
async def get_stats():
    return {
        "document_count": len(engine.documents),
        "vocabulary_size": len(engine.vectorizer.get_feature_names_out()) if engine.tfidf_matrix is not None else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
