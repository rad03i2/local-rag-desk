"""Local RAG Desk public API."""
__version__ = "1.0.0"
from .core import RagError, SearchHit, build_index, format_context, load_index, search, tokenize, validate_index
__all__ = ["RagError","SearchHit","build_index","format_context","load_index","search","tokenize","validate_index"]
