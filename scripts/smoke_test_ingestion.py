# MODULE: End-to-end smoke test for the ingestion pipeline components.
"""Verifies that PDFExtractor, Chunker, and Embedder work together."""

from __future__ import annotations

import logging
from pathlib import Path
import sys

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.ingestion.pdf_extractor import PDFExtractor
from src.ingestion.chunker import Chunker
from src.ingestion.embedder import Embedder
from src.common.logging_utils import configure_logging

def main():
    """Run a limited ingestion pass and print results."""
    configure_logging("smoke_test")
    logger = logging.getLogger("smoke_test")
    
    sample_file = PROJECT_ROOT / "tests" / "fixtures" / "sample_textual.pdf"
    if not sample_file.exists():
        print(f"❌ Error: Sample file not found at {sample_file}")
        sys.exit(1)
        
    print(f"🚀 Starting smoke test with: {sample_file.name}")
    
    # 1. Extraction
    extractor = PDFExtractor()
    print("Step 1: Extracting pages...")
    pages = extractor.extract(sample_file)
    if not pages:
        print("❌ Error: Extraction returned no pages.")
        sys.exit(1)
    print(f"✅ Extracted {len(pages)} pages.")
    
    # 2. Chunking
    chunker = Chunker()
    print("Step 2: Chunking pages...")
    chunks = chunker.chunk(pages, sample_file)
    if not chunks:
        print("❌ Error: Chunking returned no chunks.")
        sys.exit(1)
    print(f"✅ Created {len(chunks)} chunks.")
    
    # 3. Embedding (First 2 chunks)
    embedder = Embedder()
    print("Step 3: Embedding first 2 chunks (requires Ollama)...")
    try:
        to_embed = [c.text for c in chunks[:2]]
        vectors = embedder.embed_batch(to_embed)
        
        for i, vector in enumerate(vectors):
            chunk = chunks[i]
            print(f"\n--- Chunk {i+1} Metadata ---")
            print(f"Source: {chunk.source_file}")
            print(f"Page:   {chunk.page_number}")
            print(f"Domain: {chunk.domain}")
            print(f"Vector: {vector[:5]}... (dim={len(vector)})")
            
        print("\n✨ SMOKE TEST SUCCESSFUL ✨")
        
    except Exception as exc:
        print(f"❌ Embedding failed: {exc}")
        print("Note: Ensure Ollama is running and 'nomic-embed-text' model is pulled.")
        sys.exit(1)

if __name__ == "__main__":
    main()
