from app.database import get_db
from app.database.crud import set_storage_quota
from app.database.models import Base, engine

def init_quotas():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    
    # 设置默认配额 (1TB, 300GB, 100GB)
    set_storage_quota(db, 'public', 1099511627776, 1)  # 1TB
    set_storage_quota(db, 'group', 322122547200, 1)    # 300GB
    set_storage_quota(db, 'user', 107374182400, 1)     # 100GB

if __name__ == "__main__":
    init_quotas()