"""Auth Router: Token generation, user profile, persona switching."""

from fastapi import APIRouter, Depends, HTTPException, status

from apps.api.auth.security import (
    USERS_DB,
    create_access_token,
    get_current_user,
    verify_password,
)
from apps.api.schemas.models import (
    LoginRequest,
    SwitchPersonaRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    user = USERS_DB.get(req.email)
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    token = create_access_token({
        "sub": user["user_id"],
        "email": user["email"],
        "tenant_id": user["tenant_id"],
        "active_persona": user["active_persona"],
    })
    return TokenResponse(access_token=token, active_persona=user["active_persona"])


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        user_id=current_user["user_id"],
        email=current_user["email"],
        role=current_user["role"],
        tenant_id=current_user["tenant_id"],
        active_persona=current_user["active_persona"],
    )


@router.post("/switch-persona", response_model=UserResponse)
def switch_persona(req: SwitchPersonaRequest, current_user: dict = Depends(get_current_user)):
    valid_personas = ["ai_ml_engineer", "fullstack_web_dev", "data_analyst"]
    if req.persona not in valid_personas:
        raise HTTPException(status_code=400, detail=f"Invalid persona. Choose from: {valid_personas}")
    current_user["active_persona"] = req.persona
    return UserResponse(
        user_id=current_user["user_id"],
        email=current_user["email"],
        role=current_user["role"],
        tenant_id=current_user["tenant_id"],
        active_persona=req.persona,
    )
