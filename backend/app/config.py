from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Image Search API"
    environment: str = "development"
    database_url: str = (
        # Usamos el driver puro de Python pymysql para evitar compilación nativa.
        "mysql+pymysql://root:password@db:3306/image_search"
    )
    deepl_api_key: str = "3e3ebc35-340b-4533-9626-2e8aad239f95:fx"

    class Config:
        env_file = ".env"


settings = Settings()
