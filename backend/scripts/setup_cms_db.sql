USE cms_db;

-- 用户表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    role ENUM('public', 'member', 'admin') NOT NULL DEFAULT 'public',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    storage_quota BIGINT DEFAULT 1073741824, -- 默认1GB存储空间
    used_storage BIGINT DEFAULT 0
) ENGINE=InnoDB;

-- 文件系统表
CREATE TABLE files (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(255) NOT NULL,
    parent_id CHAR(36),
    is_folder BOOLEAN NOT NULL DEFAULT FALSE,
    owner_type ENUM('public', 'group', 'user') NOT NULL,
    owner_id INT NOT NULL,
    storage_path VARCHAR(512) NOT NULL,
    size BIGINT NOT NULL DEFAULT 0,
    mime_type VARCHAR(100),
    status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'approved',
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES files(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_owner (owner_type, owner_id),
    INDEX idx_parent (parent_id)
) ENGINE=InnoDB;

-- 权限表
CREATE TABLE permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id CHAR(36) NOT NULL,
    user_id INT NOT NULL,
    access_level ENUM('read', 'write', 'manage') NOT NULL,
    granted_by INT NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_file_user (file_id, user_id)
) ENGINE=InnoDB;

-- 审核日志表
CREATE TABLE moderation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id CHAR(36) NOT NULL,
    moderator_id INT NOT NULL,
    action ENUM('approve', 'reject') NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
    FOREIGN KEY (moderator_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;