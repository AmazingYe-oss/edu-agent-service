"""
用户认证 API - 登录、注册
"""

import uuid
import hashlib
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import User
from app.models.schemas import UserRegisterRequest, UserLoginRequest, UserResponse

router = APIRouter()


def hash_password(password: str) -> str:
    """密码哈希（简单实现，生产环境应使用 bcrypt）"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    return hash_password(password) == password_hash


@router.post("/register", response_model=UserResponse)
async def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册
    
    - username: 用户名（至少3位）
    - password: 密码（至少6位）
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 生成用户ID
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    
    # 创建新用户
    new_user = User(
        user_id=user_id,
        username=request.username,
        password_hash=hash_password(request.password)
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return UserResponse(
            user_id=new_user.user_id,
            username=new_user.username,
            message="注册成功"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")


@router.post("/login", response_model=UserResponse)
async def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    用户登录
    
    - username: 用户名
    - password: 密码
    """
    # 查找用户
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 验证密码
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        message="登录成功"
    )


@router.get("/user/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """获取用户信息"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        message="获取成功"
    )
