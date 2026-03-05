import os
import yaml
import sys
from typing import Literal, Optional, Any, Type, Dict
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- 1. DEFINICIJA PARAMETARA (Spec) ---
# Ovde dodaješ nove sekcije konfiguracije (npr. redis, auth, itd.)
class DbConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = Field(5432, ge=1, le=65535)
    user: str = "admin"
    password: str = "secret"

class Settings(BaseSettings):
    """
    Glavna klasa za podešavanja. 
    Pydantic Settings automatski mapira environment varijable.
    Primer: DB__PORT će pregaziti db.port vrednost.
    """
    model_config = SettingsConfigDict(
        env_nested_delimiter="__", 
        env_file=".env",
        extra="ignore"
    )

    app_env: Literal["dev", "prod", "test"] = "dev"
    debug: bool = False
    db: DbConfig = DbConfig()
    api_key: Optional[str] = None

    # --- HELPER METODE ---
    def is_env(self, env_name: str) -> bool:
        """Proverava trenutno okruženje"""
        return self.app_env == env_name

    @classmethod
    def load(cls) -> "Settings":
        """
        Glavni loader: 
        1. Prioritet 1: Environment Variables (najjači)
        2. Prioritet 2: YAML fajl (ako je ENV_YAML setovan)
        3. Prioritet 3: .env fajl
        4. Prioritet 4: Default vrednosti iz koda
        """
        yaml_data = {}
        yaml_path = os.getenv("ENV_YAML")
        
        if yaml_path:
            path = Path(yaml_path)
            if path.exists():
                with open(path, "r") as f:
                    yaml_data = yaml.safe_load(f) or {}
            else:
                print(f"⚠️ UPOZORENJE: ENV_YAML je setovan na {yaml_path}, ali fajl ne postoji.")

        try:
            # Pydantic Settings automatski spaja yaml_data sa environment varijablama
            return cls(**yaml_data)
        except ValidationError as e:
            print("\n❌ [PPICONF] Kritična greška u konfiguraciji:")
            for error in e.errors():
                loc = " -> ".join(str(v) for v in error["loc"])
                print(f"   📍 {loc}: {error['msg']} (Dobijeno: {error['input']})")
            sys.exit(1)

    def reload(self):
        """Osvežava konfiguraciju u runtime-u"""
        new_instance = self.load()
        for field in self.model_fields:
            setattr(self, field, getattr(new_instance, field))
        print("🔄 [PPICONF] Konfiguracija je uspešno osvežena.")

# --- 2. SINGLETON INSTANCA ---
# Ovo je ono što korisnik uvozi: from ppiconf import config
config = Settings.load()

# --- 3. CLI ALAT (Glue Code za tim) ---
def cli_generate():
    """Generiše template fajlove za kolege"""
    print("🛠️  Generisanje konfiguracionih primera...")
    
    # Generiši YAML primer
    with open("config.example.yaml", "w") as f:
        yaml.dump(config.model_dump(), f, default_flow_style=False)
    
    # Generiši .env primer (flat verzija)
    with open(".env.example", "w") as f:
        f.write("# PPICONF Auto-generated Example\n")
        data = config.model_dump()
        for k, v in data.items():
            if isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    f.write(f"{k.upper()}__{sub_k.upper()}={sub_v}\n")
            else:
                f.write(f"{k.upper()}={v}\n")
    
    print("✅ Kreirani: config.example.yaml i .env.example")