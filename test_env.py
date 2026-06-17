from pydantic import BaseModel, BaseSettings, Field
from dotenv import load_dotenv
import os

load_dotenv()

class APIKeys(BaseSettings):
    anthropic: str = Field(None, env="ANTHROPIC_API_KEY")

class JarvisConfig(BaseSettings):
    api_keys: APIKeys = Field(default_factory=APIKeys)

config = JarvisConfig()
print("KEY IS:", config.api_keys.anthropic)
