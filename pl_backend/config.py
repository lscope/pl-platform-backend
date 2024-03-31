from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    # Con questa classe di Pydantic facciamo una validazione automatica sulle variabili d'ambiente (in modo case-insensitive), e esplicitandone il tipo viene anche già fatta la conversione. In questo modo non dobbiamo utilizzare il metodo os.getenv(), e se una o più variabili d'ambiente mancano verrà sollevata un'eccezione.
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


settings = Settings()

DB_USERNAME = settings.postgres_user
DB_PASSWORD = settings.postgres_password
DB_HOST = settings.postgres_host
DB_NAME = settings.postgres_db

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes