from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import settings, Settings
from routers import analytics, predict, ask, upload, chat
from rag.vectorstore import get_vectorstore_manager, ensure_vectorstore_initialized
from services.data_service import get_data_service
from services.prediction_service import get_prediction_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up Financial Analytics AI System...")
    
    try:
        settings.validate()
        print("[OK] Configuration validated")
        
        data_service = get_data_service()
        print(f"[OK] Data loaded: {len(data_service.df)} transactions")
        
        print("Checking vectorstore...")
        
        import os
        chroma_db_path = os.path.join(settings.CHROMA_PERSIST_DIR, "chroma.sqlite3")
        vectorstore_exists = os.path.exists(chroma_db_path)
        
        vectorstore_manager = get_vectorstore_manager()
        vectorstore_initialized = False
        
        if vectorstore_exists:
            print(f"Found existing vectorstore at {settings.CHROMA_PERSIST_DIR}")
            print("Loading existing vectorstore...")
            try:
                vectorstore_manager.initialize_vectorstore(force_recreate=False)
                vectorstore_manager = get_vectorstore_manager()
                
                if vectorstore_manager.vectorstore is not None:
                    vectorstore_initialized = True
                    print(f"[OK] Vectorstore loaded (type: {type(vectorstore_manager.vectorstore).__name__})")
                else:
                    print("[WARNING] Vectorstore file exists but failed to load")
            except Exception as e:
                error_msg = str(e)
                print(f"[WARNING] Could not load vectorstore: {error_msg}")
                if "API key" in error_msg or "401" in error_msg:
                    print("  -> Check your API_KEY in .env")
        else:
            print("  -> No existing vectorstore found")
            print("  -> Note: Vectorstore can be created if needed")
        
        if not vectorstore_initialized:
            print("  -> Server will start, vectorstore uses lazy initialization")
        
        print("Training predictive models...")
        prediction_service = get_prediction_service()
        print("[OK] Predictive models ready")
        
        print("=" * 60)
        print("Financial Analytics AI System is ready!")
        print(f"API Documentation: http://localhost:8000/docs")
        print("=" * 60)
        
    except Exception as e:
        print(f"ERROR during startup: {e}")
        print("Please check your configuration and data files.")
        raise
    
    yield
    
    print("Shutting down...")

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ask.router)
app.include_router(chat.router)
app.include_router(analytics.router)
app.include_router(predict.router)
app.include_router(upload.router)

@app.get("/")
async def root():
    return {
        "message": "Financial Analytics & Digital Business AI System",
        "version": settings.API_VERSION,
        "status": "operational",
        "endpoints": {
            "upload": "/api/upload - Upload CSV file with transaction data",
            "ask": "/ask - Generate SQL queries from natural language",
            "analytics": {
                "revenue": "/analytics/revenue - Revenue analytics",
                "channels": "/analytics/channels - Channel performance",
                "retention": "/analytics/retention - Retention analysis"
            },
            "predictions": {
                "transactions": "/predict/transactions - Transaction volume forecast",
                "cancellation": "/predict/cancellation - Cancellation risk prediction",
                "suspicious": "/predict/suspicious - Suspicious transaction detection"
            }
        },
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    try:
        data_service = get_data_service()
        vectorstore_manager = get_vectorstore_manager()
        
        vectorstore_ready = False
        vectorstore_status = "not_initialized"
        
        if vectorstore_manager.vectorstore is None:
            try:
                vectorstore_manager.initialize_vectorstore(force_recreate=False)
                vectorstore_manager = get_vectorstore_manager()
            except Exception as init_error:
                pass
        
        if vectorstore_manager.vectorstore is not None:
            vectorstore_ready = True
            vectorstore_status = "ready"
        else:
            import os
            chroma_db_path = os.path.join(settings.CHROMA_PERSIST_DIR, "chroma.sqlite3")
            if os.path.exists(chroma_db_path):
                vectorstore_status = "exists_but_not_loaded"
            else:
                vectorstore_status = "not_created"
        
        return {
            "status": "healthy",
            "data_loaded": len(data_service.df) if data_service.df is not None else 0,
            "vectorstore_ready": vectorstore_ready,
            "vectorstore_status": vectorstore_status
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

