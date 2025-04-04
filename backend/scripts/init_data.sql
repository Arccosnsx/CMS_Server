USE cms_db;

-- 创建系统根文件夹
SET FOREIGN_KEY_CHECKS=0;

INSERT INTO files (id, name, is_folder, owner_type, owner_id, storage_path, created_by)
VALUES 
('00000000-0000-0000-0000-000000000001', 'public', TRUE, 'public', 0, '/mnt/store/public', 0),
('00000000-0000-0000-0000-000000000002', 'group', TRUE, 'group', 1, '/mnt/store/group', 0),
('00000000-0000-0000-0000-000000000003', 'users', TRUE, 'user', 0, '/mnt/store/users', 0);

SET FOREIGN_KEY_CHECKS=1;