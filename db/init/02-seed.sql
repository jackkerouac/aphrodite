-- Insert a test user (password is 'testpassword' but we'd use a proper hash in production)
INSERT INTO users (username, email, password_hash)
VALUES ('testuser', 'test@example.com', '$2a$10$rRyBsGSHK6.uc8fntPwVILYYzHsacS52qV.tHi8BPwZ15zdr6i3/G');

-- Insert default user settings for the test user
INSERT INTO user_settings (user_id, theme, language, notifications_enabled)
VALUES (1, 'dark', 'en', true);

-- Insert test Jellyfin settings for the test user
INSERT INTO jellyfin_settings (user_id, jellyfin_url, jellyfin_api_key, jellyfin_user_id)
VALUES (1, 'http://jellyfin.local:8096', 'a1b2c3d4e5f6g7h8i9j0', '1a2b3c4d5e6f7g8h9i0j');
