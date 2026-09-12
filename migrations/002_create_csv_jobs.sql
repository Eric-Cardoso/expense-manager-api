CREATE TABLE IF NOT EXISTS attached_csvs (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    status ENUM('pendente', 'processando', 'sucesso', 'erro') NOT NULL,
    attached_at DATETIME NOT NULL,
    valid BOOLEAN NOT NULL,
    
    CONSTRAINT fk_csv_user FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE RESTRICT 
)
