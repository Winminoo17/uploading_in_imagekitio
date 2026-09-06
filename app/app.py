from contextlib import asynccontextmanager
import os
import shutil
import tempfile
import uuid

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from app.db import Post, create_tables, get_session, User
from app.images import imagekit
from app.schemas import PostCreate, PostResponse, UserRead, UserCreate
from app.users import auth_backend, current_active_user, fastapi_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(lifespan=lifespan)

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserCreate),
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(current_active_user)],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(...),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session)
):
    temp_file_path = None

    try:
        # ၁။ Temp file ထဲ အရင် ကူးယူသိမ်းဆည်းပါ
        suffix = os.path.splitext(file.filename)[1] if file.filename else ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
            temp_file.flush()

        with open(temp_file_path, "rb") as f:
            upload_result = imagekit.files.upload(
                file=f,
                file_name=file.filename or str(uuid.uuid4()),
                use_unique_file_name=True,
                tags=["backend-upload"],
            )

        post = Post(
            user_id=user.id,
            caption=caption,
            url=upload_result.url,
            file_type="video" if (file.content_type or "").startswith("video") else "image",
            file_name=upload_result.name
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)
        
        return post

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        await file.close()


@app.get("/feed")  
async def get_feed(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_active_user)
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]
    posts_data = []
    result = await session.execute(select(User))
    current_user = [row[0] for row in result.all()]
    user_dict = {u.id: u.email for u in current_user}

    for post in posts:
        posts_data.append({
            "id": str(post.id),
            "user_id": str(post.user_id),
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at.isoformat(),
            "is_owner": post.user_id == user.id,
            "email": user_dict.get(post.user_id, "Unknown user")  
        })
    return {"posts": posts_data}

@app.delete("/delete/{post_id}")
async def delete_post(
    post_id: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session)
):
    try:
        post_uuid = uuid.UUID(post_id)
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalar_one_or_none()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found.")

        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post.")
        
        await session.delete(post)
        await session.commit()
        return {"message": "Post deleted successfully."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await session.close()