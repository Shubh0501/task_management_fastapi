from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.user import User
from models.role import Role, UserRoleLink
from src.database import get_db_session
from src.utils.hash_service import hash_password, verify_password
from src.utils.token_service import create_access_token, create_refresh_token, decode_refresh_token
from .structure import UserCreate, UserRead, LoginRequest, TokenResponse, RefreshRequest

router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, session: Session = Depends(get_db_session)):
    # Checking if user exists
    exists = (await session.execute(select(User).where(User.email == user.email))).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email is already registered. Please login using your details.")
    # Creating new user
    newuser = User(
        email=user.email,
        full_name=user.full_name,
        password_hash=hash_password(user.password)
    )
    session.add(newuser)
    await session.flush()
    if len(user.roles) > 0:
        roles = (await session.execute(select(Role.id).where(Role.code.in_(user.roles)))).scalars().all()
        if len(roles) > 0:
            user_role_links = [UserRoleLink(user_id=newuser.id, role_id=roleId) for roleId in roles]
            session.add_all(user_role_links)
    await session.commit()
    await session.refresh(newuser)
    return newuser


@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: LoginRequest, session: Session = Depends(get_db_session)):
    # Searching for the user in the DB
    user = (await session.execute(select(User).where(User.email == login_data.email))).scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials provided.")
    # Check and match password of the user
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password. Please try again.")

    # Generate tokens for access
    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(request: RefreshRequest):
    payload = decode_refresh_token(request.refresh_token)
    
    if payload.get("status") == "errored":
        raise HTTPException(status_code=401, detail=payload.get("message"))

    if payload.get("scope") != "refresh_token":
        raise HTTPException(status_code=401, detail="Invalid token scope provided")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token. Please login.")
    email = payload.get("email")
    new_access_token  = create_access_token({"sub": str(user_id), "email": email})
    new_refresh_token = create_refresh_token({"sub": str(user_id), "email": email})

    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)