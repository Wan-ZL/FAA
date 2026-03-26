"""Configuration management for Finance Agent.

Loads settings from config.yaml, .env, and environment variables.
Priority: Environment variables > config.yaml > defaults.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _load_yaml_config() -> dict[str, Any]:
    """Load config.yaml if it exists."""
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    return {}


_yaml = _load_yaml_config()


class LLMConfig(BaseSettings):
    """LLM model configuration."""

    model_config = SettingsConfigDict(env_prefix="FINANCE_AGENT_LLM__")

    leader_model: str = Field(
        default=_yaml.get("llm", {}).get("default_leader_model", "claude-opus-4-6")
    )
    worker_model: str = Field(
        default=_yaml.get("llm", {}).get("default_worker_model", "claude-sonnet-4-6")
    )
    router_model: str = Field(
        default=_yaml.get("llm", {}).get("default_router_model", "claude-haiku-4-5-20251001")
    )
    fallback_provider: str = Field(
        default=_yaml.get("llm", {}).get("fallback_provider", "openai/gpt-4o")
    )


class AgentConfig(BaseSettings):
    """Agent execution configuration."""

    model_config = SettingsConfigDict(env_prefix="FINANCE_AGENT_AGENTS__")

    max_concurrent: int = Field(
        default=_yaml.get("agents", {}).get("max_concurrent", 6)
    )
    max_tool_calls_per_turn: int = Field(
        default=_yaml.get("agents", {}).get("max_tool_calls_per_turn", 25)
    )


class TokenConfig(BaseSettings):
    """Token budget configuration."""

    model_config = SettingsConfigDict(env_prefix="FINANCE_AGENT_TOKENS__")

    leader_budget: int = Field(
        default=_yaml.get("tokens", {}).get("leader_budget", 32000)
    )
    worker_budget: int = Field(
        default=_yaml.get("tokens", {}).get("worker_budget", 16000)
    )
    router_budget: int = Field(
        default=_yaml.get("tokens", {}).get("router_budget", 2000)
    )


class MemoryConfig(BaseSettings):
    """Storage backend configuration."""

    model_config = SettingsConfigDict(env_prefix="FINANCE_AGENT_MEMORY__")

    neo4j_uri: str = Field(
        default=_yaml.get("memory", {}).get("neo4j_uri", "bolt://localhost:7687")
    )
    neo4j_user: str = Field(default=os.getenv("NEO4J_USER", "neo4j"))
    neo4j_password: str = Field(default=os.getenv("NEO4J_PASSWORD", ""))
    chroma_persist_dir: str = Field(
        default=_yaml.get("memory", {}).get("chroma_persist_dir", "./data/chroma")
    )
    duckdb_path: str = Field(
        default=_yaml.get("memory", {}).get("duckdb_path", "./data/timeseries.duckdb")
    )
    sqlite_board_path: str = Field(
        default=_yaml.get("memory", {}).get("sqlite_board_path", "./data/shared_board.db")
    )


class APIKeysConfig(BaseSettings):
    """API key configuration loaded from .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    anthropic_api_key: str = Field(default="")
    finnhub_api_key: str = Field(default="")
    fred_api_key: str = Field(default="")
    alpha_vantage_api_key: str = Field(default="")
    polygon_api_key: str = Field(default="")
    sec_edgar_user_agent: str = Field(default="FinanceAgent contact@example.com")


class Settings(BaseSettings):
    """Root configuration aggregating all sub-configs."""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    agents: AgentConfig = Field(default_factory=AgentConfig)
    tokens: TokenConfig = Field(default_factory=TokenConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    api_keys: APIKeysConfig = Field(default_factory=APIKeysConfig)


# Singleton
settings = Settings()
