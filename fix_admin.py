import sqlite3
import bcrypt

target_db = 'shibam_db.sqlite'
conn = sqlite3.connect(target_db)
cursor = conn.cursor()

# 1. حذف الأدمن القديم لضمان النظافة
cursor.execute("DELETE FROM user WHERE username = 'admin'")

# 2. إنشاء كلمة مرور جديدة "admin123"
hashed = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# 3. إدخال الأدمن ببيانات صحيحة 100%
cursor.execute("""
    INSERT INTO user (username, email, password_hash, full_name, role, is_active) 
    VALUES ('admin', 'admin@shibam.com', ?, 'System Admin', 'Admin', 1)
""", (hashed,))

conn.commit()
conn.close()
print("✅ Admin account has been RESET successfully!")
print("Username: admin | Password: admin123")