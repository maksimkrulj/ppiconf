import os
import yaml
import sys
import logging
from typing import Literal, Optional, Any, Type, Dict
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict



class LoggingConfig(BaseModel):
    level : Literal["DEBUG" , "INFO" , "WARNING" , "ERROR"] = "INFO"
    format : str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_to_file: bool = False
    file_path : Optional [str] = "app.log"

class Settings(BaseSettings):
    logging : LoggingConfig = LoggingConfig()

class DbConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = Field(5432, ge=1, le=65535)
    user: str = "admin"
    password: str = "secret"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__", 
        env_file=".env",
        extra="ignore"
    )
    app_env: Literal["dev", "prod", "test"] = "dev"
    debug: bool = False
    db: DbConfig = DbConfig()
    api_key: Optional[str] = None

    
    def is_env(self, env_name: str) -> bool:
        
        return self.app_env == env_name

    @classmethod
    def load(cls) -> "Settings":
        yaml_data = {}
        yaml_path = os.getenv("ENV_YAML")
        
        if yaml_path:
            path = Path(yaml_path)
            if path.exists():
                with open(path, "r") as f:
                    yaml_data = yaml.safe_load(f) or {}
            else:
                print(f" Warning : ENV_YAML is set at {yaml_path}, but the file doesnt exist.")

        try:
            
            return cls(**yaml_data)
        except ValidationError as e:
            print("\n [PPICONF] Fatal error in configuration:")
            for error in e.errors():
                loc = " -> ".join(str(v) for v in error["loc"])
                print(f"    {loc}: {error['msg']} (Dobijeno: {error['input']})")
            sys.exit(1)

    def reload(self):
        new_instance = self.load()
        for field in self.model_fields:
            setattr(self, field, getattr(new_instance, field))
        print("[PPICONF] Configuration has been refreshed.")


config = Settings.load()


def cli_generate():
    
    print("Generating conf examples...")
    
    
    with open("config.example.yaml", "w") as f:
        yaml.dump(config.model_dump(), f, default_flow_style=False)

    with open(".env.example", "w") as f:
        f.write("# PPICONF Auto-generated Example\n")
        data = config.model_dump()
        for k, v in data.items():
            if isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    f.write(f"{k.upper()}__{sub_k.upper()}={sub_v}\n")
            else:
                f.write(f"{k.upper()}={v}\n")
    
    print("Created: config.example.yaml and .env.example")

def setup_logger():
    """Logger settings"""
    logging.basicConfig(
        level=config.logging.level,
        format=config.logging.format,
        handlers=[
            logging.StreamHandler(), 
        ]
    )
     
    if config.logging.log_to_file:
        file_handler = logging.FileHandler(config.logging.file_path)
        logging.getLogger().addHandler(file_handler)
        
    logging.info(f"Logger set at level : {config.logging.level}")

setup_logger()