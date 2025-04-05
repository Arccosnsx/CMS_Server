from fastapi import APIRouter, Depends, UploadFile,Form , HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.database.models import User, File
from app.schemas.file import FileOut, FileMove
from app.schemas.file import FileCreate, FileOut, FileMove, FileStatus
from app.dependencies import get_current_active_user
from app.services.file_service import move_file,handle_merge_chunks
from app.services.permission import check_file_permission
from app.config import settings
from typing import Optional
import os

router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/upload/chunk")
async def upload_chunkupload_chunk(
    file: UploadFile,
    identifier: str = Form(...),
    chunkNumber: int = Form(...),
    chunkSize: int = Form(...),
    currentChunkSize: int = Form(...),
    totalSize: int = Form(...),
    totalChunks: int = Form(...),
    filename: str = Form(...),
    relativePath: str = Form(...),
    space_type: str = Form(...),
    parent_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """上传文件分片"""
    # 检查权限
    if parent_id:
        parent = db.query(File).filter(File.id == parent_id).first()
        if not parent or not check_file_permission(current_user, parent.owner_type, parent.owner_id):
            raise HTTPException(403, "No permission")

    # 保存分片到以MD5命名的目录
    chunk_dir = os.path.join(settings.CHUNKTEMP, identifier)
    os.makedirs(chunk_dir, exist_ok=True)
    chunk_path = os.path.join(chunk_dir, str(chunkNumber))

    with open(chunk_path, "wb") as buffer:
        buffer.write(await file.read())

    return {"message": "Chunk uploaded"}


@router.get("/upload/chunk")
async def check_chunk(
    identifier: str,  # 文件的MD5值
    chunkNumber: int,  # 当前分片编号（从1开始）
    chunkSize: int,  # 分片大小
    currentChunkSize: int,  # 当前分片实际大小
    totalSize: int,  # 文件总大小
    filename: str,  # 文件名
    relativePath: str,  # 相对路径（可选）
    totalChunks: int,  # 总分片数
    space_type: str,  # 空间类型（public/group/user）
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """检查分片是否已上传，支持断点续传"""
    # 1. 检查是否已有完整文件（秒传）
    existing_file = db.query(File).filter(
        File.md5 == identifier,
        File.size == totalSize,
        File.status == FileStatus.approved
    ).first()

    if existing_file:
        return {
            "skipUpload": True,  # 告诉前端可以秒传
            "uploaded": list(range(1, totalChunks + 1))  # 所有分片都已"上传"
        }

    # 2. 检查已上传的分片（断点续传）
    chunk_dir = os.path.join(settings.CHUNKTEMP, identifier)
    uploaded_chunks = []

    if os.path.exists(chunk_dir):
        uploaded_chunks = [
            int(chunk) 
            for chunk in os.listdir(chunk_dir) 
            if chunk.isdigit()
        ]

    # 3. 返回已上传的分片编号
    return {
        "skipUpload": False,
        "uploaded": uploaded_chunks  # 如 [1, 2, 3] 表示前3个分片已上传
    }


@router.post("/upload/merge")
async def merge_chunks(
    identifier: str = Form(...),
    filename: str = Form(...),
    space_type: str = Form(...),
    parent_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return handle_merge_chunks(identifier,filename,space_type,parent_id,db,current_user)

@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if not check_file_permission(current_user, file.owner_type, file.owner_id):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    if file.status != FileStatus.approved:
        raise HTTPException(status_code=403, detail="File not approved")
    
    if not os.path.exists(file.storage_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        file.storage_path,
        filename=file.name,
        media_type=file.mime_type
    )

@router.post("/move/{file_id}", response_model=FileOut)
async def move_file(
    file_id: str,
    move_data: FileMove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return move_file(db, file_id, move_data.target_parent_id, current_user)

@router.post("/create-folder", response_model=FileOut)
async def create_folder(
    folder_data: FileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建新文件夹"""
    if not folder_data.is_folder:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use this endpoint only for folder creation"
        )
    
    return create_folder(db, folder_data, current_user)

@router.get("/list", response_model=list[FileOut])
async def list_files(
    parent_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """列出目录内容"""
    # 根目录特殊处理
    if parent_id is None:
        root_folders = []
        
        # 所有用户都能看到公共文件夹
        public_folder = db.query(File).filter(
            File.parent_id.is_(None),
            File.owner_type == "PUBLIC",
            File.status == FileStatus.approved
        ).first()
        
        if public_folder:
            root_folders.append(public_folder)
        
        # 成员和管理员能看到社团文件夹
        if current_user.role in ("member", "admin"):
            group_folder = db.query(File).filter(
                File.parent_id.is_(None),
                File.owner_type == "GROUP",
                File.status == FileStatus.approved
            ).first()
            
            if group_folder:
                root_folders.append(group_folder)
        
        # 个人文件夹（所有登录用户）
        personal_folder = db.query(File).filter(
            File.parent_id.is_(None),
            File.owner_type == "USER",
            File.owner_id == current_user.id,
            File.status == FileStatus.approved
        ).first()
        
        if personal_folder:
            root_folders.append(personal_folder)
            
        return root_folders
    
    # 非根目录正常查询
    query = db.query(File).filter(
        File.parent_id == parent_id,
        File.status == FileStatus.approved
    )
    
    # 添加权限检查
    parent = db.query(File).filter(File.id == parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")
    
    if parent.owner_type == "user" and parent.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission")
    
    if parent.owner_type == "group" and current_user.role not in ("member", "admin"):
        raise HTTPException(status_code=403, detail="Group access requires member role")
    
    return query.all()