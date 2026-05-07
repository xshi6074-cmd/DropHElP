from pydantic_settings import BaseSettings
from typing import Optional
import sys


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/kuaibang"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120  # 默认2小时
    long_term_token_expire_days: int = 90   # 长期Token 3个月（老人端）

    # Admin Token (MVP用于内部脚本、Cronjob)
    admin_token: str = "kuaibang-admin-secret-dev"

    # SMTP (可选，开发模式控制台输出验证码)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from: Optional[str] = None

    # App
    debug: bool = True
    app_name: str = "drophelp"

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 生产环境强制检查Secret Key长度
        if not self.debug and len(self.secret_key) < 32:
            print("[FATAL] 生产环境JWT_SECRET_KEY必须至少32字符")
            sys.exit(1)


settings = Settings()
