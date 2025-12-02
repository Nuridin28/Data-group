from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.schemas import SQLRequest, SQLResponse, QuestionResponse
from services.data_service import get_data_service
from rag.rag_chain import get_rag_chain

router = APIRouter(prefix="/ask", tags=["SQL Generation & AI Questions"])

@router.post("", response_model=SQLResponse)
async def ask_question(request: SQLRequest) -> SQLResponse:
    try:
        question = request.question if hasattr(request, 'question') and request.question else ""
        
        if not question or not question.strip():
            raise HTTPException(status_code=400, detail="Question is required")
        
        data_service = get_data_service()
        rag_chain = get_rag_chain()
        
        try:
            table_schema = data_service.get_table_schema()
            result = rag_chain.generate_sql_query(question, table_schema)
            
            return SQLResponse(
                sql_query=result.get("sql_query", ""),
                explanation=result.get("explanation", result.get("answer", "No explanation available")),
                table_name=result.get("table_name", "transactions")
            )
        except Exception as sql_error:
            result = rag_chain.query(question, use_rag=True)
            answer = result.get("answer", "Не удалось получить ответ")
            
            return SQLResponse(
                sql_query="",
                explanation=answer,
                table_name="transactions"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

