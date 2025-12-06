from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    NEON_DB: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_JWT_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
        validate_default=False,
    )

    @property
    def online_url(self):
        return self.NEON_DB


settings = DBSettings()
