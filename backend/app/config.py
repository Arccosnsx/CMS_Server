from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "mariadb+mariadbconnector://cms_user:CMSDatabase!15937asd@localhost/cms_db"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CMSDatabase!15937asd")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    PUBLIC_ROOT:str ="/mnt/store/public"
    GROUP_ROOT:str ="/mnt/store/group"
    USER_ROOT:str ="/mnt/store/users"
    CHUNKTEMP:str ="/mnt/store/chunk_temp"

    class Config:
        env_file = ".env"
        extra = "ignore"  # 忽略额外字段

settings = Settings()