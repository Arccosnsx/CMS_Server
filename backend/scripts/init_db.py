import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, User

DATABASE_URL = "mariadb+mariadbconnector://cms_user:StrongPass123!@localhost/cms_db"

def init_database():
    # 创建表结构
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    
    # 初始化管理员账户
    Session = sessionmaker(bind=engine)
    db = Session()
    
    if not db.query(User).filter_by(username="admin").first():
        hashed_pw = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())
        admin = User(
            username="admin",
            password_hash=hashed_pw.decode(),
            role="admin"
        )
        db.add(admin)
        db.commit()
    
    db.close()

if __name__ == "__main__":
    init_database()
    print("✅ 数据库初始化完成")