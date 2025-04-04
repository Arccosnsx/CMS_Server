import mariadb

try:
    conn = mariadb.connect(
        user="cms_user",
        password="CMSDatabase!15937asd",
        host="localhost",
        database="cms_db"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users")
    for (username, role) in cursor:
        print(f"User: {username}, Role: {role}")
    conn.close()
    print("✅ 数据库连接测试成功")
except mariadb.Error as e:
    print(f"❌ 数据库连接错误: {e}")