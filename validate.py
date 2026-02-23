#!/usr/bin/env python
"""Quick validation script to check if all imports work correctly."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("RUSS RAG Tutor - Import Validation")
print("=" * 60)

try:
    print("\n[1/6] Importing schemas...")
    from src.models.schemas import (
        Document, DocumentStatus, Chunk, MessageRole, ChatMessage,
        ConversationSession, Subject, Citation, SafetyCheckResult, RetrievalResult
    )
    print("✓ Schemas imported successfully")
except Exception as e:
    print(f"✗ Failed to import schemas: {e}")
    sys.exit(1)

try:
    print("[2/6] Importing settings...")
    from src.config.settings import settings
    print(f"✓ Settings loaded (Ollama URL: {settings.ollama_base_url})")
except Exception as e:
    print(f"✗ Failed to import settings: {e}")
    sys.exit(1)

try:
    print("[3/6] Importing config prompts...")
    from src.config.prompts import RAG_SYSTEM_PROMPT, SAFETY_BLOCK_RESPONSE
    print("✓ Prompts imported successfully")
except Exception as e:
    print(f"✗ Failed to import prompts: {e}")
    sys.exit(1)

try:
    print("[4/6] Importing core modules...")
    from src.ingestion.pipeline import ingest_document
    from src.generation.rag_chain import ask_question
    from src.generation.llm_client import check_ollama_health
    from src.retrieval.hybrid_retriever import HybridRetriever
    print("✓ Core modules imported successfully")
except Exception as e:
    print(f"✗ Failed to import core modules: {e}")
    sys.exit(1)

try:
    print("[5/6] Importing utilities...")
    from src.utils.helpers import collection_name_for_file, is_pdf, validate_file_size
    print("✓ Utilities imported successfully")  
except Exception as e:
    print(f"✗ Failed to import utilities: {e}")
    sys.exit(1)

try:
    print("[6/6] Checking Ollama health...")
    health = check_ollama_health()
    if health.get("ok"):
        print(f"✓ Ollama is running! Available models: {health.get('available')}")
    else:
        print(f"⚠ Ollama is not running. To start: ollama serve")
        print(f"  Missing models: {health.get('missing')}")
except Exception as e:
    print(f"⚠ Could not check Ollama health: {e}")

print("\n" + "=" * 60)
print("✓ All imports successful! Application is ready.")
print("=" * 60)
print("\nTo start the Streamlit app, run:")
print("  streamlit run app.py")
print("\nTo ensure Ollama is running, open another terminal and run:")
print("  ollama serve")
print("=" * 60)
