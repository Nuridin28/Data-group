import os
from typing import List, Dict, Any, Optional
import pandas as pd
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import settings

class VectorStoreManager:
    
    def __init__(self):
        embedding_kwargs = {"model": settings.EMBEDDING_MODEL}
        
        # Для embeddings нужен OpenAI API key, не DeepSeek
        # Используем OPENAI_API_KEY если есть, иначе пробуем API_KEY
        embedding_api_key = settings.OPENAI_API_KEY or settings.API_KEY
        if embedding_api_key:
            embedding_kwargs["openai_api_key"] = embedding_api_key
        
        try:
            self.embeddings = OpenAIEmbeddings(**embedding_kwargs)
        except Exception as e:
            print(f"Warning: Could not initialize embeddings: {str(e)[:100]}")
            # Если embeddings не инициализированы, vectorstore не будет работать
            # но это не критично - есть CSV fallback
            self.embeddings = None
        self.vectorstore = None
        self.collection_name = "financial_transactions"
        
    def _load_and_preprocess_data(self) -> pd.DataFrame:
        if not os.path.exists(settings.DATA_FILE):
            raise FileNotFoundError(f"Data file not found: {settings.DATA_FILE}")
        
        df = pd.read_csv(settings.DATA_FILE)
        
        df = df.fillna("")
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        return df
    
    def _row_to_text(self, row: pd.Series) -> str:
        text_parts = []
        
        if 'transaction_id' in row:
            text_parts.append(f"Transaction ID: {row['transaction_id']}")
        if 'date' in row and pd.notna(row['date']):
            text_parts.append(f"Date: {row['date']}")
        if 'region' in row and row['region']:
            text_parts.append(f"Region: {row['region']}")
        if 'city' in row and row['city']:
            text_parts.append(f"City: {row['city']}")
        if 'merchant_id' in row:
            text_parts.append(f"Merchant ID: {row['merchant_id']}")
        if 'merchant_category' in row and row['merchant_category']:
            text_parts.append(f"Merchant Category: {row['merchant_category']}")
        if 'channel' in row and row['channel']:
            text_parts.append(f"Channel: {row['channel']}")
        if 'payment_method' in row and row['payment_method']:
            text_parts.append(f"Payment Method: {row['payment_method']}")
        if 'customer_segment' in row and row['customer_segment']:
            text_parts.append(f"Customer Segment: {row['customer_segment']}")
        if 'acquisition_source' in row and row['acquisition_source']:
            text_parts.append(f"Acquisition Source: {row['acquisition_source']}")
        if 'device_type' in row and row['device_type']:
            text_parts.append(f"Device Type: {row['device_type']}")
        if 'amount_kzt' in row and pd.notna(row['amount_kzt']):
            text_parts.append(f"Amount: {row['amount_kzt']} KZT")
        if 'is_refunded' in row:
            text_parts.append(f"Refunded: {'Yes' if row['is_refunded'] == 1 else 'No'}")
        if 'is_canceled' in row:
            text_parts.append(f"Canceled: {'Yes' if row['is_canceled'] == 1 else 'No'}")
        if 'delivery_time_hours' in row and pd.notna(row['delivery_time_hours']) and row['delivery_time_hours'] != '':
            text_parts.append(f"Delivery Time: {row['delivery_time_hours']} hours")
        if 'suspicious_flag' in row:
            text_parts.append(f"Suspicious: {'Yes' if row['suspicious_flag'] == 1 else 'No'}")
        
        return ". ".join(text_parts) + "."
    
    def initialize_vectorstore(self, force_recreate: bool = False) -> None:
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        
        chroma_db_path = os.path.join(settings.CHROMA_PERSIST_DIR, "chroma.sqlite3")
        if not force_recreate and os.path.exists(chroma_db_path):
            try:
                print(f"Attempting to load existing vectorstore from {settings.CHROMA_PERSIST_DIR}...")
                if self.embeddings is None:
                    raise ValueError("Embeddings not initialized - needs OpenAI API key")
                
                self.vectorstore = Chroma(
                    persist_directory=settings.CHROMA_PERSIST_DIR,
                    embedding_function=self.embeddings,
                    collection_name=self.collection_name
                )
                if self.vectorstore is not None:
                    if hasattr(self.vectorstore, 'similarity_search_with_score'):
                        print(f"[OK] Loaded existing vectorstore from {settings.CHROMA_PERSIST_DIR}")
                        return
                    else:
                        print(f"Warning: Vectorstore loaded but missing similarity_search_with_score method")
                        print(f"[OK] Loaded existing vectorstore (method check skipped)")
                        return
                else:
                    raise ValueError("Failed to load vectorstore - Chroma returned None")
            except Exception as e:
                error_msg = str(e)
                # Скрываем детали API ключа
                if "API key" in error_msg or "401" in error_msg or "invalid_api_key" in error_msg or "Incorrect API key" in error_msg:
                    # Проверяем что это ошибка embeddings
                    if "embedding" in error_msg.lower() or "openai" in error_msg.lower():
                        print("Warning: Failed to load vectorstore - embeddings need OpenAI API key (DeepSeek key doesn't work for embeddings). Using CSV fallback.")
                    else:
                        print("Warning: Failed to load vectorstore due to API key issue. Using CSV fallback.")
                else:
                    print(f"Warning: Failed to load existing vectorstore: {error_msg[:200]}")
                # Не показываем полный traceback для API ошибок
                if "API key" not in error_msg and "401" not in error_msg and "Incorrect API key" not in error_msg:
                    import traceback
                    traceback.print_exc()
                print("Will use CSV fallback for data retrieval...")
                force_recreate = False
                self.vectorstore = None
        
        if force_recreate or not os.path.exists(chroma_db_path):
            if self.embeddings is None:
                print("Cannot create vectorstore: embeddings not initialized (needs OpenAI API key)")
                print("Note: DeepSeek API key doesn't work for embeddings. Set OPENAI_API_KEY in .env for vectorstore.")
                self.vectorstore = None
                return
            
            print("Creating new vectorstore...")
            print("WARNING: This will create embeddings for ~30,000 rows via OpenAI API.")
            print("This may take 10-15 minutes and will use API credits.")
            print("Note: Requires OPENAI_API_KEY (DeepSeek key doesn't work for embeddings)")
            print("Please wait...")
            df = self._load_and_preprocess_data()
            print(f"Loaded {len(df)} rows from CSV")
            
            documents = []
            metadatas = []
            
            for idx, row in df.iterrows():
                text = self._row_to_text(row)
                
                def safe_int(val, default=0):
                    try:
                        return int(val) if pd.notna(val) and val != '' else default
                    except (ValueError, TypeError):
                        return default
                
                def safe_float(val, default=0.0):
                    try:
                        return float(val) if pd.notna(val) and val != '' else default
                    except (ValueError, TypeError):
                        return default
                
                def safe_str(val, default=''):
                    try:
                        return str(val) if pd.notna(val) and val != '' else default
                    except (ValueError, TypeError):
                        return default
                
                doc = Document(
                    page_content=text,
                    metadata={
                        "transaction_id": safe_int(row.get('transaction_id', idx), int(idx)),
                        "date": safe_str(row.get('date', '')),
                        "region": safe_str(row.get('region', '')),
                        "city": safe_str(row.get('city', '')),
                        "merchant_id": safe_int(row.get('merchant_id', 0)),
                        "merchant_category": safe_str(row.get('merchant_category', '')),
                        "channel": safe_str(row.get('channel', '')),
                        "payment_method": safe_str(row.get('payment_method', '')),
                        "customer_segment": safe_str(row.get('customer_segment', '')),
                        "amount_kzt": safe_float(row.get('amount_kzt', 0)),
                        "is_refunded": safe_int(row.get('is_refunded', 0)),
                        "is_canceled": safe_int(row.get('is_canceled', 0)),
                        "suspicious_flag": safe_int(row.get('suspicious_flag', 0)),
                        "row_index": int(idx)
                    }
                )
                documents.append(doc)
                metadatas.append(doc.metadata)
            
            try:
                print(f"Creating embeddings for {len(documents)} documents via API...")
                print("This may take several minutes. Please be patient...")
                if self.embeddings is None:
                    raise ValueError("Embeddings not initialized - needs OpenAI API key")
                
                self.vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=settings.CHROMA_PERSIST_DIR,
                    collection_name=self.collection_name
                )
                print(f"[OK] Created vectorstore with {len(documents)} documents")
                print("Vectorstore is now ready for queries!")
                if self.vectorstore is None:
                    raise ValueError("Failed to create vectorstore")
            except Exception as e:
                error_msg = str(e)
                if "API key" in error_msg or "401" in error_msg or "embedding" in error_msg.lower():
                    print(f"Error creating vectorstore: Embeddings need OpenAI API key (DeepSeek key doesn't work for embeddings)")
                    print("Note: Set OPENAI_API_KEY in .env for vectorstore, or use CSV fallback")
                else:
                    print(f"Error creating vectorstore: {error_msg[:200]}")
                # Не показываем полный traceback для API ошибок
                if "API key" not in error_msg and "401" not in error_msg:
                    import traceback
                    traceback.print_exc()
                raise
    
    def search(self, query: str, k: int = None) -> List[Dict[str, Any]]:
        # Проверяем что embeddings доступны
        if self.embeddings is None:
            raise ValueError("Embeddings not available - needs OpenAI API key. DeepSeek key doesn't work for embeddings.")
        
        if self.vectorstore is None:
            chroma_db_path = os.path.join(settings.CHROMA_PERSIST_DIR, "chroma.sqlite3")
            if not os.path.exists(chroma_db_path):
                raise ValueError("Vectorstore not found. Needs OpenAI API key to create embeddings.")
            try:
                self.initialize_vectorstore(force_recreate=False)
            except Exception as e:
                error_msg = str(e)
                if "API key" in error_msg or "embedding" in error_msg.lower():
                    raise ValueError("Vectorstore needs OpenAI API key for embeddings. DeepSeek key is for LLM only.")
                raise ValueError(f"Vectorstore not initialized and failed to initialize: {e}")
        
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized. Call initialize_vectorstore() first.")
        
        k = k or settings.RAG_TOP_K
        
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            })
        
        return formatted_results
    
    def get_vectorstore(self) -> Chroma:
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized. Call initialize_vectorstore() first.")
        return self.vectorstore

_vectorstore_manager = None

def get_vectorstore_manager() -> VectorStoreManager:
    global _vectorstore_manager
    if _vectorstore_manager is None:
        _vectorstore_manager = VectorStoreManager()
    return _vectorstore_manager

def ensure_vectorstore_initialized() -> bool:
    global _vectorstore_manager
    if _vectorstore_manager is None:
        _vectorstore_manager = VectorStoreManager()
    
    if _vectorstore_manager.vectorstore is None:
        chroma_db_path = os.path.join(settings.CHROMA_PERSIST_DIR, "chroma.sqlite3")
        if not os.path.exists(chroma_db_path):
            print("Note: Creating vectorstore for the first time. This may take 10-15 minutes.")
        try:
            _vectorstore_manager.initialize_vectorstore(force_recreate=False)
        except Exception as e:
            print(f"Warning: Failed to initialize vectorstore: {e}")
            return False
    
    return _vectorstore_manager.vectorstore is not None
