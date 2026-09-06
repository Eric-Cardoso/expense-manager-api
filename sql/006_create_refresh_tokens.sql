CREATE TABLE IF NOT EXISTS refresh_tokens (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    token_hash VARCHAR(80) NOT NULL UNIQUE,
    is_revoked BOOLEAN NOT NULL,
    expiration_date DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    
    CONSTRAINT fk_refresh_token_user FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE RESTRICT 
)
