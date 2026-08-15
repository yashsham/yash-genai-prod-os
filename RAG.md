## RAG Security & Retrieval Rules

- **Metadata-based access**  
  All document retrieval must be filtered using metadata (tenant, role, sensitivity level) before vector similarity search is performed.

- **Encrypted vectors**  
  Embeddings stored in the vector database must be encrypted at rest and protected in transit using TLS.

- **Similarity threshold enforced**  
  Retrieved documents must meet a minimum similarity score. Low-confidence context must be rejected to prevent hallucinations and data leakage.

- **Context window limits**  
  Strict limits must be enforced on the number of documents and total tokens injected into the LLM context window.
