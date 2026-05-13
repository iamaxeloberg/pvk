from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    low_cost_llm_model: str = "deepseek/deepseek-chat"
    low_cost_llm_api_key: str = ""
    low_cost_llm_api_base: str = ""

    high_capacity_llm_model: str = "anthropic/claude-3-5-sonnet-20241022"
    high_capacity_llm_api_key: str = ""

    db_path: str = "data/quantera.db"
    input_dir: str = "data/input"
    markdown_dir: str = "data/markdown"

    temperature: float = 0.0
    max_tokens: int = 4096

    chunk_size: int = 4000
    chunk_overlap: int = 200

    max_doc_size_chars: int = 100000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def db_path_obj(self) -> Path:
        return Path(self.db_path)

    @property
    def input_dir_obj(self) -> Path:
        return Path(self.input_dir)

    @property
    def markdown_dir_obj(self) -> Path:
        return Path(self.markdown_dir)


settings = Settings()
