from dataclasses import dataclass

from decouple import config


def _parse_admins(raw_admins: str) -> set[int]:
    admins: set[int] = set()
    for chunk in raw_admins.split(","):
        value = chunk.strip()
        if value.isdigit():
            admins.add(int(value))
    return admins


@dataclass(frozen=True)
class Settings:
    token: str
    database_dsn: str
    database_enabled: bool
    admins: set[int]


def load_settings() -> Settings:
    token = config("TOKEN", default="").strip()
    if not token:
        raise RuntimeError("TOKEN is empty in .env")

    database_dsn = config("DATABASE_DSN", default=config("PG_LOGIN", default="")).strip()
    admins_raw = config("ADMINS", default="")
    admins = _parse_admins(admins_raw)

    return Settings(
        token=token,
        database_dsn=database_dsn,
        database_enabled=False,  # Temporary local mode without database
        admins=admins,
    )


settings = load_settings()
