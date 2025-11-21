#!/usr/bin/env python
"""Test DeepSeek configuration."""
from config.config import settings
from rag.rag_chain import get_rag_chain
from rag.vectorstore import get_vectorstore_manager

print("=== DeepSeek Configuration Test ===")
print(f"API_KEY: {settings.API_KEY[:30] + '...' if settings.API_KEY else 'None'}")
print(f"API_BASE_URL: {settings.API_BASE_URL}")
print(f"LLM_MODEL: {settings.LLM_MODEL}")
print(f"EMBEDDING_MODEL: {settings.EMBEDDING_MODEL}")
print()

print("Initializing components...")
try:
    rag = get_rag_chain()
    print("✓ RAG chain initialized")
    print(f"  LLM will use: {settings.LLM_MODEL} at {settings.API_BASE_URL or 'OpenAI default'}")
    
    vm = get_vectorstore_manager()
    print("✓ Vectorstore manager initialized")
    print(f"  Embeddings will use: {settings.EMBEDDING_MODEL} at OpenAI")
    
    print()
    print("SUCCESS: Configuration is ready for DeepSeek!")
    print()
    print("Note: DeepSeek is used for LLM (chat), OpenAI is used for embeddings")
    print("If embeddings fail, you may need a separate OpenAI API key")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

