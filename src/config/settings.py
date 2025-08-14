"""Environment and configuration management (lightweight).

Uses python-dotenv to read a local `.env` file when present. Avoids heavy
dependencies to keep imports fast during tests.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv, find_dotenv


# Load environment variables from the nearest .env, if present.
# `find_dotenv()` walks up parent directories so the file can live at repo root
# or within subpackages. This keeps behavior stable regardless of where the
# CLI/script is invoked from.
load_dotenv(dotenv_path=find_dotenv(usecwd=True), override=False)


@dataclass(frozen=True)
class Settings:
    """Typed application settings with sensible defaults.

    Keep this small and reference here from all modules to ensure consistency.
    """

    # General
    pipeline_version: str = os.getenv("PIPELINE_VERSION", "0.1.0")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    language: str = os.getenv("LANGUAGE", "en")

    # Limits and thresholds
    token_cap_per_step: int = int(os.getenv("TOKEN_CAP_PER_STEP", "140"))
    near_duplicate_cosine: float = float(os.getenv("NEAR_DUPLICATE_COSINE", "0.9"))

    # Embeddings model (lazy-load in code paths, do not import on module import)
    embedding_model_name: str = os.getenv(
        "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
    )

    # Local LLM settings (Qwen2.5:3B-instruct via Ollama or similar)
    use_local_llm: bool = os.getenv("USE_LOCAL_LLM", "true").lower() in {"1", "true", "yes"}
    local_llm_endpoint: str = os.getenv(
        "LOCAL_LLM_ENDPOINT", "http://localhost:11434/api/generate"
    )
    local_llm_model: str = os.getenv("LOCAL_LLM_MODEL", "qwen2.5:3b-instruct")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))

    # CLI-only persistence (for now) — where to write artifacts during dev
    output_dir: str = os.getenv("OUTPUT_DIR", "./.out")

    # Database
    # Example (Neon): postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
    database_url: str = os.getenv("DATABASE_URL", "")
    # Source table for Step 1 fetch. Defaults to `lesson_dirty` (page-level rows
    # with `page_content` JSON that we flatten in-app).
    db_table_raw_sections: str = os.getenv("DB_TABLE_RAW_SECTIONS", "lesson_dirty")

    # Classifier (Step 3) configuration
    classifier_use_llm_fallback: bool = os.getenv("CLASSIFIER_USE_LLM_FALLBACK", "true").lower() in {"1", "true", "yes"}
    classifier_score_threshold: float = float(os.getenv("CLASSIFIER_SCORE_THRESHOLD", "0.55"))
    classifier_margin_threshold: float = float(os.getenv("CLASSIFIER_MARGIN_THRESHOLD", "0.10"))
    classifier_max_llm_calls_per_section: int = int(os.getenv("CLASSIFIER_MAX_LLM_CALLS_PER_SECTION", "3"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return process-wide cached settings instance."""
    return Settings()


