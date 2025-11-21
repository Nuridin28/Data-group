from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import settings
from rag.vectorstore import get_vectorstore_manager, ensure_vectorstore_initialized

class RAGChain:
    
    def __init__(self):
        import os
        # Set environment variables to avoid langchain.verbose/debug attribute errors
        os.environ.setdefault("LANGCHAIN_VERBOSE", "false")
        os.environ.setdefault("LANGCHAIN_DEBUG", "false")
        
        llm_kwargs = {
            "model": settings.LLM_MODEL,
            "temperature": float(settings.TEMPERATURE) if settings.TEMPERATURE else 0.0,
            "callbacks": [],  # Disable callbacks to avoid langchain attribute errors
        }
        
        api_key = settings.API_KEY
        if api_key:
            llm_kwargs["openai_api_key"] = api_key
        
        if settings.API_BASE_URL:
            base_url = settings.API_BASE_URL.rstrip('/')
            if not base_url.endswith('/v1'):
                base_url = base_url + '/v1'
            llm_kwargs["base_url"] = base_url
        
        try:
            if not api_key:
                raise ValueError("API_KEY is not set. Please set API_KEY in .env file.")
            
            # Try to initialize LLM, handle langchain version issues
            try:
                self.llm = ChatOpenAI(**llm_kwargs)
            except (AttributeError, TypeError) as e:
                error_str = str(e)
                if "verbose" in error_str or "debug" in error_str or "has no attribute" in error_str:
                    # Remove problematic parameters and try with minimal config
                    minimal_kwargs = {
                        "model": llm_kwargs.get("model"),
                        "openai_api_key": llm_kwargs.get("openai_api_key"),
                        "base_url": llm_kwargs.get("base_url"),
                        "temperature": llm_kwargs.get("temperature"),
                    }
                    self.llm = ChatOpenAI(**{k: v for k, v in minimal_kwargs.items() if v is not None})
                else:
                    raise
            
            print(f"[OK] LLM initialized: {settings.LLM_MODEL} at {settings.API_BASE_URL}")
        except ImportError as e:
            print(f"Warning: langchain_openai not installed: {str(e)[:100]}")
            self.llm = None
        except Exception as e:
            error_msg = str(e)
            if "API key" in error_msg or "401" in error_msg or "invalid" in error_msg.lower():
                print(f"Warning: Invalid API key or authentication error. Check API_KEY in .env")
            else:
                print(f"Warning: Could not initialize LLM: {str(e)[:100]}")
            self.llm = None
        
        self.vectorstore_manager = get_vectorstore_manager()
        self._vectorstore_warning_shown = False  # Флаг чтобы показывать предупреждение только раз
        
        self.system_prompt = """You are an expert financial analyst and AI assistant specialized in digital economy analytics for Kazakhstan.

Your expertise includes:
- Transaction data analysis and fraud detection
- Revenue forecasting and trend analysis
- Customer retention and segmentation
- Channel performance optimization
- Risk assessment and anomaly detection

CRITICAL INSTRUCTIONS:
1. Always answer based on the provided dataset context - be data-driven
2. NEVER invent numbers, dates, or statistics not in the provided data
3. If data is insufficient, clearly state what can and cannot be determined
4. Show your analytical reasoning and calculations
5. For fraud/anomaly detection, explain WHY transactions are suspicious
6. Provide actionable business insights and recommendations
7. Use professional analytical language with specific metrics
8. Compare segments, channels, and time periods when relevant
9. Identify patterns, trends, and anomalies with clear explanations
10. Always specify the time period, filters, and data scope you're analyzing

Response format for professional analysis:
- Direct answer with key findings
- Specific numbers, percentages, and metrics from data
- Clear explanation of patterns and anomalies
- Actionable recommendations
- Risk assessment with reasoning
- Context: dates, regions, categories, segments"""
    
    def _format_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        if not retrieved_docs:
            return "No relevant data found."
        
        context_parts = []
        context_parts.append("Relevant transaction data from the dataset:\n")
        
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(f"Data point {i}:")
            context_parts.append(doc['content'])
            if doc.get('metadata'):
                meta = doc['metadata']
                context_parts.append(f"Metadata: Transaction ID {meta.get('transaction_id', 'N/A')}, "
                                    f"Date: {meta.get('date', 'N/A')}, "
                                    f"City: {meta.get('city', 'N/A')}, "
                                    f"Amount: {meta.get('amount_kzt', 0)} KZT")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def query(self, question: str, use_rag: bool = True, top_k: int = None) -> Dict[str, Any]:
        retrieved_docs = []
        
        if use_rag:
            try:
                if ensure_vectorstore_initialized():
                    retrieved_docs = self.vectorstore_manager.search(question, k=top_k or settings.RAG_TOP_K)
                    if retrieved_docs:
                        context = self._format_context(retrieved_docs)
                    else:
                        raise ValueError("No results from vectorstore")
                else:
                    raise ValueError("Vectorstore not initialized")
            except Exception as e:
                error_msg = str(e)
                # Скрываем детали API ключа из ошибок
                if "API key" in error_msg or "401" in error_msg or "invalid_api_key" in error_msg or "Incorrect API key" in error_msg:
                    if not self._vectorstore_warning_shown:
                        # Проверяем что это ошибка embeddings (OpenAI), а не DeepSeek
                        if "embedding" in error_msg.lower() or "openai" in error_msg.lower():
                            print("Note: Embeddings service unavailable (needs OpenAI API key for vectorstore). Using CSV fallback for data retrieval.")
                        else:
                            print("Note: Vectorstore unavailable (API key issue). Using CSV fallback for data retrieval.")
                        self._vectorstore_warning_shown = True
                    error_msg = "API key issue - using CSV fallback"
                else:
                    # Логируем только краткое сообщение, не полный traceback
                    if not self._vectorstore_warning_shown:
                        print(f"Vectorstore not available, using CSV fallback: {error_msg[:100]}")
                        self._vectorstore_warning_shown = True
                
                try:
                    from services.data_service import get_data_service
                    data_service = get_data_service()
                    retrieved_docs = data_service.get_relevant_data_for_question(
                        question, 
                        limit=(top_k or settings.RAG_TOP_K) * 10
                    )
                    context = self._format_context(retrieved_docs)
                    if not retrieved_docs:
                        context = "No relevant data found in dataset based on question keywords."
                except Exception as fallback_error:
                    print(f"CSV fallback also failed: {fallback_error}")
                    context = "Unable to retrieve data from dataset. Please check data availability."
        else:
            context = "No specific context provided. Answer based on general knowledge about financial analytics."
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Context from dataset:
{context}

Question: {question}

Please provide a comprehensive answer based strictly on the provided context. If the context doesn't contain enough information to fully answer the question, state what can be determined from the available data and what cannot.""")
        ]
        
        if self.llm is None:
            return {
                "answer": "AI service is not available. Please check API_KEY in .env file and ensure langchain-openai is installed.",
                "sources": retrieved_docs
            }
        
        response = self.llm.invoke(messages)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        sources = []
        for doc in retrieved_docs:
            sources.append({
                "content": doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content'],
                "metadata": doc.get('metadata', {}),
                "relevance_score": doc.get('score', 0)
            })
        
        return {
            "answer": answer,
            "sources": sources,
            "num_sources": len(sources)
        }
    
    def query_with_analytics(self, question: str, data_summary: Dict[str, Any] = None) -> Dict[str, Any]:
        retrieved_docs = []
        
        try:
            if ensure_vectorstore_initialized():
                retrieved_docs = self.vectorstore_manager.search(question, k=settings.RAG_TOP_K)
                if retrieved_docs:
                    context = self._format_context(retrieved_docs)
                else:
                    raise ValueError("No results from vectorstore")
            else:
                raise ValueError("Vectorstore not initialized")
        except Exception as e:
            error_msg = str(e)
            # Скрываем детали API ключа из ошибок
            if "API key" in error_msg or "401" in error_msg or "invalid_api_key" in error_msg or "Incorrect API key" in error_msg:
                if not self._vectorstore_warning_shown:
                    # Проверяем что это ошибка embeddings (OpenAI), а не DeepSeek
                    if "embedding" in error_msg.lower() or "openai" in error_msg.lower():
                        print("Note: Embeddings service unavailable (needs OpenAI API key for vectorstore). Using CSV fallback for data retrieval.")
                    else:
                        print("Note: Vectorstore unavailable (API key issue). Using CSV fallback for data retrieval.")
                    self._vectorstore_warning_shown = True
                error_msg = "API key issue - using CSV fallback"
            else:
                # Логируем только краткое сообщение
                if not self._vectorstore_warning_shown:
                    print(f"Vectorstore not available, using CSV fallback: {error_msg[:100]}")
                    self._vectorstore_warning_shown = True
            
            try:
                from services.data_service import get_data_service
                data_service = get_data_service()
                retrieved_docs = data_service.get_relevant_data_for_question(
                    question, 
                    limit=settings.RAG_TOP_K * 10
                )
                context = self._format_context(retrieved_docs) if retrieved_docs else "No relevant data found in dataset."
            except Exception as fallback_error:
                print(f"CSV fallback also failed: {fallback_error}")
                context = "Unable to retrieve data from dataset. Using provided analytics summary only."
        
        summary_text = ""
        if data_summary:
            summary_text = f"\n\nAdditional Analytics Summary:\n"
            for key, value in data_summary.items():
                summary_text += f"{key}: {value}\n"
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""Context from dataset:
{context}
{summary_text}

Question: {question}

Provide a comprehensive analysis based on the provided data.""")
        ]
        
        if self.llm is None:
            return {
                "answer": "AI service is not available. Please check API_KEY in .env file and ensure langchain-openai is installed.",
                "sources": retrieved_docs
            }
        
        response = self.llm.invoke(messages)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        sources = []
        for doc in retrieved_docs:
            sources.append({
                "content": doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content'],
                "metadata": doc.get('metadata', {}),
                "relevance_score": doc.get('score', 0)
            })
        
        return {
            "answer": answer,
            "sources": sources,
            "num_sources": len(sources)
        }

    def generate_sql_query(self, question: str, table_schema: Dict[str, Any]) -> Dict[str, Any]:
        sql_system_prompt = """You are a SQL query generator specialized in financial transaction data analysis.

Your task is to generate valid SQL queries based on natural language questions about the transactions table.

CRITICAL RULES:
1. Generate ONLY valid SQL SELECT queries
2. Use the exact column names from the schema provided
3. For city names, use exact values from sample_cities (e.g., 'Almaty', 'Astana', 'Shymkent')
4. For boolean fields (is_refunded, is_canceled, suspicious_flag), use 0 or 1, not true/false
5. For date comparisons, use proper SQL date format: 'YYYY-MM-DD'
6. Always filter out refunded and canceled transactions unless specifically asked about them
7. Use COUNT(*) for counting transactions
8. Use SUM(amount_kzt) for total revenue
9. Use AVG(amount_kzt) for average amounts
10. Use GROUP BY for aggregations by city, channel, category, etc.
11. Use WHERE for filtering conditions
12. Use LIKE for partial string matching if needed
13. Return ONLY the SQL query, no explanations in the query itself
14. Use table name: transactions

Response format:
- Generate clean, valid SQL query
- Use proper SQL syntax
- Include appropriate WHERE, GROUP BY, ORDER BY clauses
- Handle city name variations: Алматы/Алмата/Almaty -> 'Almaty', Астана/Astana -> 'Astana', Шымкент/Shymkent -> 'Shymkent'
- Always use English city names from sample_cities list"""

        schema_text = f"""Table Schema: {table_schema['table_name']}
Total rows: {table_schema['total_rows']}

Columns:
"""
        for col in table_schema['columns']:
            schema_text += f"- {col['name']}: {col['type']}"
            if col.get('sample_values') and len(col['sample_values']) > 0:
                samples = col['sample_values'][:5]
                schema_text += f" (examples: {', '.join(map(str, samples))})"
            schema_text += "\n"
        
        if table_schema.get('sample_cities'):
            schema_text += f"\nSample cities in data: {', '.join(map(str, table_schema['sample_cities'][:15]))}\n"
        if table_schema.get('sample_channels'):
            schema_text += f"Sample channels: {', '.join(map(str, table_schema['sample_channels'][:10]))}\n"
        if table_schema.get('sample_categories'):
            schema_text += f"Sample categories: {', '.join(map(str, table_schema['sample_categories'][:10]))}\n"
        
        messages = [
            SystemMessage(content=sql_system_prompt),
            HumanMessage(content=f"""Table Schema:
{schema_text}

Question: {question}

Generate a SQL SELECT query to answer this question. Return ONLY the SQL query, no additional text.""")
        ]
        
        if self.llm is None:
            # Возвращаем простой SQL запрос как fallback
            return {
                "sql_query": f"SELECT * FROM {table_schema.get('table_name', 'transactions')} LIMIT 100",
                "explanation": "AI service unavailable. Please check API_KEY in .env file and ensure langchain-openai is installed. Returning basic query.",
                "table_name": table_schema.get('table_name', 'transactions')
            }
        
        response = self.llm.invoke(messages)
        sql_query = response.content if hasattr(response, 'content') else str(response)
        
        sql_query = sql_query.strip()
        
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        sql_query = sql_query.strip()
        
        sql_query = sql_query.replace('\n', ' ')
        sql_query = sql_query.replace('\r', ' ')
        while '  ' in sql_query:
            sql_query = sql_query.replace('  ', ' ')
        
        if sql_query.endswith(';'):
            sql_query = sql_query[:-1]
        sql_query = sql_query.strip()
        
        explanation_prompt = f"""Explain what this SQL query does in one sentence:

{sql_query}

Question: {question}

Provide a brief explanation."""
        
        # Генерируем объяснение
        try:
            explanation_response = self.llm.invoke([
                SystemMessage(content="You are a SQL query explainer. Provide concise explanations."),
                HumanMessage(content=explanation_prompt)
            ])
            explanation = explanation_response.content if hasattr(explanation_response, 'content') else str(explanation_response)
        except Exception as e:
            explanation = f"SQL query for: {question}"
        
        return {
            "sql_query": sql_query,
            "explanation": explanation.strip(),
            "table_name": table_schema['table_name']
        }

_rag_chain = None

def get_rag_chain() -> RAGChain:
    global _rag_chain
    if _rag_chain is None:
        _rag_chain = RAGChain()
    return _rag_chain

