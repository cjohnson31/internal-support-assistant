"""Phase 0 smoke test — run with: python smoke_test.py"""
from src.llm import complete, embed

print("Testing LLM completion...")
answer = complete("Say 'Phase 0 complete' and nothing else.")
print(f"  Response: {answer}")

print("\nTesting embeddings (first load is slow — ~30s)...")
vecs = embed(["hello world", "test embedding"])
print(f"  Embedding dim: {len(vecs[0])}, count: {len(vecs)}")

print("\nPhase 0 DONE")
