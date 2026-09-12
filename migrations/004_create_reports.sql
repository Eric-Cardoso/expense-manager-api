CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    total_value DECIMAL(10,2) NOT NULL DEFAULT(0),
    total_expenses INTEGER NOT NULL,
    settled_expenses INTEGER NOT NULL,
    overdue_expenses INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    CONSTRAINT fk_report_user FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE RESTRICT 
)
