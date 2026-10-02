"""Student tutoring and admin controls. Identity always comes from the JWT."""


from fastapi import APIRouter, Depends, HTTPException

from ego_server import ai
from ego_server.ai_config import AISettings, public_settings, save_settings
from ego_server.ai_models import (
    AccessUpdate,
    AIAccount,
    CreditRequest,
    MessageRequest,
    SessionCreate,
)
from ego_server.deps import CurrentUser, DbDep, require_role


router = APIRouter(dependencies=[Depends(require_role("student"))])
admin_router = APIRouter(dependencies=[Depends(require_role("admin"))])


@admin_router.get("/settings")
async def get_config(db: DbDep):
    return public_settings(db)


@admin_router.put("/settings")
async def put_config(body: AISettings, db: DbDep):
    return save_settings(db, body)


@router.get("/me", response_model=AIAccount)
async def get_access(db: DbDep, user: CurrentUser):
    return ai.account(db, user["sub"])


@router.post("/sessions")
async def create_session(body: SessionCreate, db: DbDep, user: CurrentUser):
    return ai.create_session(db, user["sub"], body)


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, db: DbDep, user: CurrentUser):
    return ai.session_view(db, user["sub"], session_id)


@router.post("/sessions/{session_id}/messages")
async def send_message(session_id: str, body: MessageRequest, db: DbDep, user: CurrentUser):
    return await ai.send_message(db, user["sub"], session_id, body)


@router.get("/submissions")
async def get_submissions(db: DbDep, user: CurrentUser):
    return ai.submission_views(db, user["sub"])


@admin_router.get("/students/{student_id}", response_model=AIAccount)
async def get_student_access(student_id: str, db: DbDep):
    return ai.account(db, student_id)


@admin_router.put("/students/{student_id}", response_model=AIAccount)
async def update_access(student_id: str, body: AccessUpdate, db: DbDep):
    ai.account(db, student_id)
    db.execute(
        """INSERT INTO ai_accounts (student_id, enabled, defense_required) VALUES (?, ?, ?)
        ON CONFLICT(student_id) DO UPDATE SET enabled = excluded.enabled,
        defense_required = excluded.defense_required""",
        (student_id, int(body.enabled), int(body.defense_required)),
    )
    db.commit()
    return ai.account(db, student_id)


@admin_router.post("/students/{student_id}/credits", response_model=AIAccount)
async def add_credit(student_id: str, body: CreditRequest, db: DbDep, user: CurrentUser):
    ai.account(db, student_id)
    amount = int(body.amount_usd * 1_000_000)
    try:
        db.execute("INSERT OR IGNORE INTO ai_accounts (student_id) VALUES (?)", (student_id,))
        existing = db.execute(
            "SELECT amount FROM ai_credits WHERE student_id = ? AND request_id = ?",
            (student_id, body.request_id),
        ).fetchone()
        if existing and existing["amount"] != amount:
            raise HTTPException(
                409, "Этот идентификатор пополнения уже использован с другой суммой"
            )
        if not existing:
            db.execute(
                "INSERT INTO ai_credits VALUES (?, ?, ?, ?, ?)",
                (student_id, body.request_id, amount, user["sub"], ai.now()),
            )
            db.execute(
                "UPDATE ai_accounts SET balance = balance + ? WHERE student_id = ?",
                (amount, student_id),
            )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return ai.account(db, student_id)


@admin_router.get("/students/{student_id}/usage")
async def get_usage(student_id: str, db: DbDep):
    ai.account(db, student_id)
    rows = db.execute(
        "SELECT * FROM ai_usage WHERE student_id = ? ORDER BY id DESC LIMIT 100", (student_id,)
    ).fetchall()
    return [{**dict(row), "cost_usd": ai.money(row["cost"])} for row in rows]


@admin_router.get("/students/{student_id}/submissions")
async def get_student_submissions(student_id: str, db: DbDep):
    ai.account(db, student_id)
    return ai.submission_views(db, student_id)
