CREATE TABLE IF NOT EXISTS expenses	(
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    csv_id INTEGER NULL,
    title VARCHAR(50) NOT NULL,
    description TEXT NULL,
    category VARCHAR(50) NOT NULL,
    status ENUM('pendente', 'pagando', 'quitado', 'atrasado') NOT NULL,
    value DECIMAL(10,2) NOT NULL DEFAULT(0),
    in_installments BOOLEAN NOT NULL,
    number_installments INTEGER NULL,
    register_date DATETIME NOT NULL,
    maturity_date DATETIME NOT NULL,
    
    CONSTRAINT fk_expense_user FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE RESTRICT,

    CONSTRAINT fk_expense_csv FOREIGN KEY (csv_id)
    REFERENCES attached_csvs(id)
    ON DELETE RESTRICT
)

