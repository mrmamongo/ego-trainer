"""Auth router — реализация в задаче ego-trainer-bmh.2.

Сейчас заглушки, возвращающие 501 Not Implemented.
"""

from fastapi import APIRouter, HTTPException, status

from ego_server.models import LoginRequest, TokenResponse


router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest) -> TokenResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="auth implemented in bmh.2",
    )


@router.post("/register", response_model=TokenResponse)
async def register(body: LoginRequest) -> TokenResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="auth implemented in bmh.2",
    )
