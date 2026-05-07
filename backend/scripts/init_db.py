#!/usr/bin/env python3
"""
数据库初始化脚本
使用方法（从项目根目录）:
    python backend/scripts/init_db.py
"""
import sys
import os

# 获取项目路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
SRC_DIR = os.path.join(BACKEND_DIR, 'src')

# 切换到backend目录
os.chdir(BACKEND_DIR)

# 将src添加到路径开头
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# 先导入config
from config import settings

# 然后导入其他模块
from database import Base


async def init_database():
    """初始化数据库表结构"""
    print(f"Connecting to database...")
    print(f"URL: {settings.database_url.replace('://', '://***:***@')}")

    engine = create_async_engine(
        settings.database_url,
        echo=False
    )

    try:
        # 测试连接
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✓ Database connection successful!")

        # 创建所有表
        async with engine.begin() as conn:
            print("Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("✓ Tables created successfully!")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(init_database())
        print("\n✓ Database initialization complete!")
    except Exception as e:
        print(f"\n✗ Failed to initialize database: {e}")
        sys.exit(1)

    input("\nPress Enter to exit...")
