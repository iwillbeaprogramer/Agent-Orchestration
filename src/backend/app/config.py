from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    cors_origins: list[str] = field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )
    yahoo_api_timeout: float = 5.0
    cache_ttl_seconds: int = 60


settings = Settings()
