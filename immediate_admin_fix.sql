-- IMMEDIATE FIX for Django Admin Charset Issue
-- Run these commands in cPanel phpMyAdmin to fix the admin panel error

-- Fix Django admin log table (this fixes your immediate issue)
ALTER TABLE `fammkoqw_amstack_db`.`django_admin_log` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `fammkoqw_amstack_db`.`django_admin_log` MODIFY `object_repr` VARCHAR(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `fammkoqw_amstack_db`.`django_admin_log` MODIFY `change_message` LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Fix other Django system tables
ALTER TABLE `fammkoqw_amstack_db`.`django_session` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `fammkoqw_amstack_db`.`django_content_type` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `fammkoqw_amstack_db`.`auth_permission` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Fix blog tables
ALTER TABLE `fammkoqw_amstack_db`.`blog_category` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `fammkoqw_amstack_db`.`blog_category` MODIFY `name` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `fammkoqw_amstack_db`.`blog_category` MODIFY `slug` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

ALTER TABLE `fammkoqw_amstack_db`.`blog_post` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `fammkoqw_amstack_db`.`blog_post` MODIFY `title` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `fammkoqw_amstack_db`.`blog_post` MODIFY `content` LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `fammkoqw_amstack_db`.`blog_post` MODIFY `excerpt` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `fammkoqw_amstack_db`.`blog_post` MODIFY `slug` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Fix user tables
ALTER TABLE `fammkoqw_amstack_db`.`accounts_user` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `fammkoqw_amstack_db`.`accounts_user` MODIFY `email` VARCHAR(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `fammkoqw_amstack_db`.`accounts_user` MODIFY `full_name` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

ALTER TABLE `fammkoqw_amstack_db`.`accounts_profile` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE `fammkoqw_amstack_db`.`accounts_profile` MODIFY `bio` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;