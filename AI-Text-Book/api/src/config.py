"""
Environment configuration for RAG-Powered Textbook Chatbot.
"""

from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# =========================
# OpenAI Configuration
# =========================
class OpenAIConfig(BaseSettings):
    api_key: str = Field(default="", alias="OPENAI_API_KEY")
    org_id: str = Field(default="", alias="OPENAI_ORG_ID")
    embedding_model: str = Field(default="text-embedding-3-large", alias="OPENAI_EMBEDDING_MODEL")
    chat_model: str = Field(default="gpt-4", alias="OPENAI_CHAT_MODEL")
    fallback_model: str = Field(default="gpt-3.5-turbo", alias="OPENAI_FALLBACK_MODEL")

    @field_validator("api_key", mode="after")
    @classmethod
    def validate_api_key(cls, v):
        """Validate API key is provided."""
        if not v:
            raise ValueError("OPENAI_API_KEY is required")
        return v

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", validate_default=False)


# =========================
# Qdrant Configuration
# =========================
class QdrantConfig(BaseSettings):
    url: str = Field(default="", alias="QDRANT_URL")
    api_key: str = Field(default="", alias="QDRANT_API_KEY")
    collection_name: str = Field(default="textbook_chunks", alias="QDRANT_COLLECTION_NAME")
    vector_size: int = Field(default=3072, alias="QDRANT_VECTOR_SIZE")
    distance: Literal["Cosine", "Dot", "Euclid"] = Field(default="Cosine", alias="QDRANT_DISTANCE")
    hnsw_m: int = Field(default=16, alias="QDRANT_HNSW_M")
    hnsw_ef_construct: int = Field(default=100, alias="QDRANT_HNSW_EF_CONSTRUCT")

    @field_validator("url", "api_key", mode="after")
    @classmethod
    def validate_required_fields(cls, v, info):
        """Validate required Qdrant fields are provided."""
        if not v:
            raise ValueError(f"{info.field_name.upper()} is required for Qdrant configuration")
        return v

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", validate_default=False)


# =========================
# Postgres Configuration
# =========================
class PostgresConfig(BaseSettings):
    url: str = Field(default="", alias="DATABASE_URL")
    host: str = Field(default="", alias="POSTGRES_HOST")
    port: int = Field(default=5432, alias="POSTGRES_PORT")
    database: str = Field(default="", alias="POSTGRES_DB")
    user: str = Field(default="", alias="POSTGRES_USER")
    password: str = Field(default="", alias="POSTGRES_PASSWORD")
    ssl_mode: str = Field(default="require", alias="POSTGRES_SSL_MODE")
    pool_min: int = Field(default=2, alias="POSTGRES_POOL_MIN")
    pool_max: int = Field(default=10, alias="POSTGRES_POOL_MAX")

    @field_validator("url", mode="after")
    @classmethod
    def validate_database_config(cls, v, info):
        """Ensure either DATABASE_URL or individual components are provided."""
        url = v
        host = info.data.get("host", "")
        database = info.data.get("database", "")
        user = info.data.get("user", "")
        password = info.data.get("password", "")

        # If DATABASE_URL is provided, use it
        if url:
            return url

        # Otherwise, require individual components
        if not all([host, database, user, password]):
            raise ValueError(
                "Either DATABASE_URL or all of (POSTGRES_HOST, POSTGRES_DB, "
                "POSTGRES_USER, POSTGRES_PASSWORD) must be provided"
            )
        return url

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", validate_default=False)


# =========================
# App Configuration
# =========================
class AppConfig(BaseSettings):
    env: Literal["development", "staging", "production"] = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="APP_DEBUG")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO", alias="APP_LOG_LEVEL")
    port: int = Field(default=8000, alias="APP_PORT")
    host: str = Field(default="0.0.0.0", alias="APP_HOST")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# =========================
# CORS Configuration
# =========================
class CORSConfig(BaseSettings):
    origins: list[str] = Field(default=["http://localhost:3000"], alias="CORS_ORIGINS")
    allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")
    allow_methods: list[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"], alias="CORS_ALLOW_METHODS")
    allow_headers: list[str] = Field(default=["Content-Type", "Authorization", "X-Request-ID"], alias="CORS_ALLOW_HEADERS")

    @field_validator("origins", "allow_methods", "allow_headers", mode="before")
    @classmethod
    def parse_csv_to_list(cls, v):
        """Parse comma-separated string to list if needed."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# =========================
# Rate Limit Configuration
# =========================
class RateLimitConfig(BaseSettings):
    anonymous: int = Field(default=10, alias="RATE_LIMIT_ANONYMOUS")
    authenticated: int = Field(default=100, alias="RATE_LIMIT_AUTHENTICATED")
    premium: int = Field(default=1000, alias="RATE_LIMIT_PREMIUM")
    burst_multiplier: int = Field(default=2, alias="RATE_LIMIT_BURST_MULTIPLIER")
    burst_duration: int = Field(default=10, alias="RATE_LIMIT_BURST_DURATION")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# =========================
# RAG Configuration
# =========================
class RAGConfig(BaseSettings):
    top_k_candidates: int = Field(default=20, alias="RAG_TOP_K_CANDIDATES")
    top_n_final: int = Field(default=5, alias="RAG_TOP_N_FINAL")
    similarity_threshold: float = Field(default=0.7, alias="RAG_SIMILARITY_THRESHOLD")
    context_window_limit: int = Field(default=8000, alias="RAG_CONTEXT_WINDOW_LIMIT")
    chunk_size: int = Field(default=1024, alias="RAG_CHUNK_SIZE")
    chunk_overlap: int = Field(default=128, alias="RAG_CHUNK_OVERLAP")

    @field_validator("similarity_threshold")
    @classmethod
    def validate_threshold(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Similarity threshold must be between 0 and 1")
        return v

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# =========================
# Sentry Configuration
# =========================
class SentryConfig(BaseSettings):
    dsn: str = Field(default="", alias="SENTRY_DSN")
    environment: str = Field(default="development", alias="SENTRY_ENVIRONMENT")
    traces_sample_rate: float = Field(default=0.1, alias="SENTRY_TRACES_SAMPLE_RATE")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# =========================
# Feature Flags
# =========================
class FeatureFlagsConfig(BaseSettings):
    general_knowledge_mode: bool = Field(default=False, alias="FEATURE_GENERAL_KNOWLEDGE_MODE")
    tone_customization: bool = Field(default=True, alias="FEATURE_TONE_CUSTOMIZATION")
    key_term_highlighting: bool = Field(default=True, alias="FEATURE_KEY_TERM_HIGHLIGHTING")
    grounding_validation: bool = Field(default=True, alias="FEATURE_GROUNDING_VALIDATION")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# =========================
# Main Settings
# =========================
class Settings(BaseSettings):

    openai: OpenAIConfig = Field(default_factory=lambda: OpenAIConfig())
    qdrant: QdrantConfig = Field(default_factory=lambda: QdrantConfig())
    postgres: PostgresConfig = Field(default_factory=lambda: PostgresConfig())

    app: AppConfig = Field(default_factory=AppConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    sentry: SentryConfig = Field(default_factory=SentryConfig)
    features: FeatureFlagsConfig = Field(default_factory=FeatureFlagsConfig)

    session_retention_days: int = Field(default=90, alias="SESSION_RETENTION_DAYS")
    analytics_enabled: bool = Field(default=True, alias="ANALYTICS_ENABLED")
    feedback_enabled: bool = Field(default=True, alias="FEEDBACK_ENABLED")

    dev_mock_vector_db: bool = Field(default=False, alias="DEV_MOCK_VECTOR_DB")
    dev_mock_llm: bool = Field(default=False, alias="DEV_MOCK_LLM")
    dev_skip_auth: bool = Field(default=False, alias="DEV_SKIP_AUTH")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def is_production(self) -> bool:
        return self.app.env == "production"

    @property
    def is_development(self) -> bool:
        return self.app.env == "development"


# Lazy singleton - only instantiate when needed
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create the settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# For backward compatibility - will be lazy loaded on first access
try:
    settings = get_settings()
except Exception:
    # If env vars not set during import, defer to runtime
    settings = None  # type: ignore
