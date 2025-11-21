from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
import pandas as pd
import os
import sys
import uuid
from pathlib import Path
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import settings
from services.data_service import reload_data_service

router = APIRouter(prefix="/api", tags=["File Upload"])

# Хранилище загруженных файлов
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Файл для хранения метаданных загруженных файлов
METADATA_FILE = UPLOAD_DIR / "uploads_metadata.json"

def load_metadata() -> Dict[str, Dict[str, Any]]:
    """Загрузить метаданные загруженных файлов"""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_metadata(metadata: Dict[str, Dict[str, Any]]):
    """Сохранить метаданные"""
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

@router.post("/upload")
async def upload_csv_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Загрузка CSV файла с транзакционными данными
    
    Принимает CSV файл, сохраняет его и возвращает file_id для последующих запросов
    """
    # Проверяем что это CSV файл
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400, 
            detail="Только CSV файлы поддерживаются. Пожалуйста, загрузите файл с расширением .csv"
        )
    
    try:
        # Генерируем уникальный ID для файла
        file_id = str(uuid.uuid4())
        
        # Сохраняем файл
        file_path = UPLOAD_DIR / f"{file_id}.csv"
        
        # Читаем содержимое файла
        contents = await file.read()
        
        # Сохраняем на диск
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        # Проверяем что файл валидный CSV
        try:
            df = pd.read_csv(file_path)
            
            # Проверяем минимальные требования к данным
            if len(df) == 0:
                os.remove(file_path)
                raise HTTPException(
                    status_code=400,
                    detail="Файл пустой. Пожалуйста, загрузите файл с данными."
                )
            
            # Сохраняем информацию о файле
            metadata = load_metadata()
            metadata[file_id] = {
                "file_path": str(file_path),
                "filename": file.filename,
                "rows": len(df),
                "columns": list(df.columns),
                "uploaded_at": pd.Timestamp.now().isoformat()
            }
            save_metadata(metadata)
            
            # Перезагружаем data service с загруженным файлом
            try:
                reload_data_service(str(file_path))
                print(f"Data service reloaded with uploaded file: {file_path}")
            except Exception as reload_error:
                print(f"Warning: Could not reload data service: {reload_error}")
                # Продолжаем работу даже если не удалось перезагрузить
            
            return {
                "message": "Файл успешно загружен и обработан",
                "file_id": file_id,
                "rows": len(df),
                "columns": list(df.columns),
                "filename": file.filename
            }
            
        except pd.errors.EmptyDataError:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail="Файл пустой или поврежден"
            )
        except pd.errors.ParserError as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail=f"Ошибка при парсинге CSV: {str(e)}"
            )
        except HTTPException:
            raise
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка при обработке файла: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при загрузке файла: {str(e)}"
        )

@router.get("/upload/{file_id}/info")
async def get_file_info(file_id: str) -> Dict[str, Any]:
    """Получить информацию о загруженном файле"""
    metadata = load_metadata()
    
    if file_id not in metadata:
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    file_info = metadata[file_id]
    file_path = file_info.get("file_path")
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл был удален")
    
    return {
        "file_id": file_id,
        "filename": file_info.get("filename"),
        "rows": file_info.get("rows", 0),
        "columns": file_info.get("columns", []),
        "uploaded_at": file_info.get("uploaded_at"),
        "file_path": file_path
    }