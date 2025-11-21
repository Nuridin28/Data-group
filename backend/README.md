# Financial Analytics & Digital Business AI System

A production-ready FastAPI backend with RAG (Retrieval-Augmented Generation) for financial analytics on Kazakhstan's digital economy transaction data.

## Features

- **RAG Pipeline**: LangChain + ChromaDB for context-aware AI responses
- **Financial Analytics**: Revenue trends, channel comparison, retention analysis
- **Predictive Models**: Transaction volume forecasting, cancellation prediction, suspicious transaction detection
- **AI-Powered Insights**: GPT-4 based analysis with strict dataset grounding
- **Production-Ready**: Modular architecture, error handling, comprehensive API

## Project Structure

```
.
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables template
├── config/
│   ├── __init__.py
│   └── config.py          # Configuration management
├── data/
│   └── track_1_digital_economy_kz.csv  # Transaction dataset
├── models/
│   ├── __init__.py
│   └── schemas.py         # Pydantic request/response models
├── rag/
│   ├── __init__.py
│   ├── vectorstore.py     # ChromaDB vector store management
│   └── rag_chain.py       # RAG chain with LangChain
├── routers/
│   ├── __init__.py
│   ├── ask.py             # Question answering endpoint
│   ├── analytics.py       # Analytics endpoints
│   └── predict.py         # Prediction endpoints
├── services/
│   ├── __init__.py
│   ├── data_service.py    # Data loading and preprocessing
│   └── prediction_service.py  # Predictive models
└── vectorstore/           # ChromaDB persistent storage (auto-created)
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file from the example:

```bash
cp env.example .env
```

Edit `.env` and add your API key (OpenAI or DeepSeek):

**For DeepSeek:**
```
API_KEY=sk-your-deepseek-key
API_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
EMBEDDING_MODEL=text-embedding-3-small
```

**For OpenAI:**
```
API_KEY=sk-your-openai-key
# Leave API_BASE_URL empty for OpenAI
LLM_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small
```

**Note:** 
- LLM uses DeepSeek API (`deepseek-chat`) via `API_KEY` and `API_BASE_URL`
- Embeddings use OpenAI API (`text-embedding-3-small`) via `OPENAI_API_KEY` (falls back to `API_KEY` if not set)
- If DeepSeek key doesn't work with OpenAI embeddings, set a separate `OPENAI_API_KEY` in `.env`

### 3. Prepare Data

Ensure your CSV file is in the `data/` folder. The file should be named `track_1_digital_economy_kz.csv` or update the `DATA_FILE` in `.env`.

### 4. Run the Application

```bash
uvicorn main:app --reload
```

The server will start on `http://localhost:8000`

- API Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Question Answering

**POST `/ask`**
- Ask questions about the financial data
- Uses RAG to retrieve relevant context
- Returns AI-generated answers based strictly on dataset

```json
{
  "question": "What are the top performing cities by revenue?"
}
```

### Analytics

**POST `/analytics/revenue`**
- Revenue trends and city/channel performance
- Includes AI insights

**POST `/analytics/channels`**
- Channel performance comparison
- AI recommendations for optimization

**POST `/analytics/retention`**
- Customer retention analysis
- Segment and acquisition source performance

### Predictions

**POST `/predict/transactions`**
- Forecast transaction volume and revenue
- Time series based predictions

**POST `/predict/cancellation`**
- Predict cancellation probability for transactions
- Risk assessment and recommendations

**POST `/predict/suspicious`**
- Detect suspicious/anomalous transactions
- Anomaly detection with AI analysis

## How It Works

### RAG Pipeline

1. **Data Loading**: CSV is loaded and preprocessed
2. **Embedding**: Each transaction row is converted to text and embedded
3. **Vector Store**: Embeddings stored in ChromaDB (persistent)
4. **Retrieval**: User queries retrieve top-K similar transactions
5. **Generation**: LLM generates answers using retrieved context
6. **Grounding**: System prompt enforces strict dataset adherence

### Predictive Models

- **Transaction Volume**: Time series analysis with trend detection
- **Cancellation Risk**: Random Forest classifier on transaction features
- **Suspicious Detection**: Isolation Forest for anomaly detection

## System Prompt

The AI is instructed to:
- Answer strictly based on provided dataset
- Never invent numbers or statistics
- Ground all insights in retrieved data
- Provide actionable recommendations
- Specify data limitations when applicable

## Notes

- First run will create the vectorstore (may take a few minutes for 30K rows)
- Vectorstore is persistent - subsequent runs are faster
- Set `TEMPERATURE=0.0` for deterministic responses
- Adjust `RAG_TOP_K` to control context size

## Production Considerations

- Set specific CORS origins in `main.py`
- Use environment-specific `.env` files
- Add authentication/authorization
- Implement rate limiting
- Add logging and monitoring
- Use production ASGI server (gunicorn + uvicorn workers)
- Set up database for user sessions if needed


