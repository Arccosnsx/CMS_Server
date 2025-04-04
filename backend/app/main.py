from fastapi import FastAPI
from app.routers import auth, files, admin, moderation
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# 后续添加其他路由
# app.include_router(files.router, prefix="/files")
# app.include_router(admin.router, prefix="/admin")
app.include_router(auth.router)
app.include_router(files.router)
app.include_router(admin.router)
app.include_router(moderation.router)

@app.get("/")
def read_root():
    return {"message": "CMS API Service"}