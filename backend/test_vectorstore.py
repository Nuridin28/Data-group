#!/usr/bin/env python
"""Test script to verify vectorstore loading."""
from rag.vectorstore import get_vectorstore_manager
from config.config import settings

def test_vectorstore():
    print("Testing vectorstore loading...")
    print(f"API Key set: {bool(settings.OPENAI_API_KEY)}")
    print(f"Vectorstore path: {settings.CHROMA_PERSIST_DIR}")
    
    vm = get_vectorstore_manager()
    print(f"Before init - vectorstore is None: {vm.vectorstore is None}")
    
    try:
        vm.initialize_vectorstore(force_recreate=False)
        print(f"After init - vectorstore is None: {vm.vectorstore is None}")
        
        if vm.vectorstore is not None:
            print(f"Type: {type(vm.vectorstore).__name__}")
            print(f"Has search method: {hasattr(vm.vectorstore, 'similarity_search_with_score')}")
            print("SUCCESS: Vectorstore loaded")
        else:
            print("WARNING: Vectorstore is None after initialization")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vectorstore()

