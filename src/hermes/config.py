from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")
    elasticsearch_url: str = Field("http://localhost:9200", env="ELASTICSEARCH_URL")
    ollama_url: str = Field("http://localhost:11434", env="OLLAMA_URL")
    ollama_model: str = Field("llama3", env="OLLAMA_MODEL")
    gliner_model: str = Field("urchade/gliner_small-v2.1", env="GLINER_MODEL")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
