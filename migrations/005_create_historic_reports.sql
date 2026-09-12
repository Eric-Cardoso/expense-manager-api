CREATE TABLE IF NOT EXISTS historic_reports	(
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    month_report VARCHAR(25) NOT NULL,
    spent_value DECIMAL(10,2) NOT NULL DEFAULT(0),
    spent_expenses INTEGER NOT NULL,
    settled_expenses INTEGER NOT NULL,
    overdue_expenses INTEGER NOT NULL,
    generated_at DATETIME NOT NULL,
    
    CONSTRAINT fk_historic_report_user FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE RESTRICT 
)
