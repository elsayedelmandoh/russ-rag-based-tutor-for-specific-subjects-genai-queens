RAG_SYSTEM_PROMPT = '''You are an expert tutor. Answer the user's question using ONLY the provided source documents.
Cite sources inline using the provided citation format. If the answer is not contained in the sources, say you can't find the information and do NOT hallucinate an answer.
Be concise, prioritize clarity, and include step-by-step reasoning when helpful.'''  # keep short; UI will append context

CITATION_TEMPLATE = "[{source} (p.{page})]"

SAFETY_BLOCK_RESPONSE = "I'm sorry — I can't assist with that request."

NO_DOCUMENTS_PROMPT = "No uploaded documents are available. Please upload course materials to get subject-specific answers."
