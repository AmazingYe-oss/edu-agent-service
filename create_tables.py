"""
数据库表创建脚本
运行此脚本可以创建所有数据库表
"""

from app.core.database import engine, Base
from app.models.domain import User, Session, UserProfile, ErrorBook


def create_tables():
    """创建所有数据库表"""
    print("正在创建数据库表...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    print("数据库表创建完成！")
    print("已创建的表:")
    print("  - users")
    print("  - sessions")
    print("  - user_profiles")
    print("  - error_books")


if __name__ == "__main__":
    create_tables()
