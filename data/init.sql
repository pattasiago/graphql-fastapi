-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- Tabela de posts
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);

-- Inserindo dados de exemplo
INSERT INTO users (name, email) VALUES
('João Silva', 'joao@example.com'),
('Maria Oliveira', 'maria@example.com');

INSERT INTO posts (title, content, user_id) VALUES
('Primeiro Post', 'Conteúdo do primeiro post', 1),
('Segundo Post', 'Conteúdo do segundo post', 2);
