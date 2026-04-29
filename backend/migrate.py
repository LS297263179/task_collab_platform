"""Run this script to migrate new columns to existing MySQL database.
Usage: python migrate.py
"""
import pymysql

conn = pymysql.connect(host='localhost', port=3306, user='root', password='123456', database='task_collab')
cursor = conn.cursor()

def add_column(table, column, definition):
    try:
        cursor.execute(f"SELECT {column} FROM {table} LIMIT 0")
        print(f"  {table}.{column} already exists")
    except:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        conn.commit()
        print(f"  + Added {table}.{column}")

print("Adding new columns to tasks table...")
add_column('tasks', 'severity', "ENUM('low','medium','high','urgent') DEFAULT 'medium' NOT NULL")
add_column('tasks', 'reproduction_steps', 'TEXT DEFAULT NULL')
add_column('tasks', 'environment', "VARCHAR(255) DEFAULT ''")
add_column('tasks', 'related_bug_ids', 'JSON DEFAULT NULL')
add_column('tasks', 'commit_hash', "VARCHAR(40) DEFAULT ''")

print("\nCreating notifications table...")
try:
    cursor.execute("SELECT 1 FROM notifications LIMIT 0")
    print("  notifications table already exists")
except:
    cursor.execute("""
        CREATE TABLE notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            message VARCHAR(500) NOT NULL,
            task_id INT DEFAULT NULL,
            is_read BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL,
            INDEX idx_user_read (user_id, is_read)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    conn.commit()
    print("  + Created notifications table")

print("\nCreating audit_logs table...")
try:
    cursor.execute("SELECT 1 FROM audit_logs LIMIT 0")
    print("  audit_logs table already exists")
except:
    cursor.execute("""
        CREATE TABLE audit_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            action VARCHAR(50) NOT NULL,
            entity_type VARCHAR(50) NOT NULL,
            entity_id INT NOT NULL,
            changes JSON DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_entity (entity_type, entity_id),
            INDEX idx_user (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    conn.commit()
    print("  + Created audit_logs table")

print("\nCreating attachments table...")
try:
    cursor.execute("SELECT 1 FROM attachments LIMIT 0")
    print("  attachments table already exists")
except:
    cursor.execute("""
        CREATE TABLE attachments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            task_id INT NOT NULL,
            filename VARCHAR(255) NOT NULL,
            original_name VARCHAR(255) NOT NULL,
            file_size INT DEFAULT 0,
            mime_type VARCHAR(100) DEFAULT '',
            uploader_id INT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
            FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_task (task_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    conn.commit()
    print("  + Created attachments table")

cursor.close()
conn.close()
print("\nDone!")
