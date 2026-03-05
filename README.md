# ppiconf 🛠️

**ppiconf** (Python Project Intelligent Config) je strogo tipizirana biblioteka za upravljanje konfiguracijom, dizajnirana posebno za Dockerizovane aplikacije. Rešava problem konfiguracije "jednom zauvek" koristeći Pydantic za validaciju i deterministički pristup za punu IDE podršku (autocomplete).

## Glavne prednosti
 **Single Source of Truth**: Konfiguracija se definiše u kodu (Python klase).
 **Type Safety**: IDE prepoznaje svako polje. Zaboravi na nagađanje naziva iz `.env` fajlova.
 **Fail-Fast**: Aplikacija se gasi pri startu ako konfiguracija nije ispravna.
 **Docker Optimized**: Podržava `ENV_YAML` za masovno učitavanje i standardne environment varijable za specifične override-ove.

---

## Instalacija

Dok si u korenom folderu projekta, instaliraj ga lokalno:
```bash
pip install -e .