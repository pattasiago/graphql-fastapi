-- Tabela de usuários
CREATE TABLE IF NOT EXISTS "Users" (
    "Id" SERIAL PRIMARY KEY,
    "Name" VARCHAR(100) NOT NULL,
    "Email" VARCHAR(100) UNIQUE NOT NULL,
    "CreatedAt" TIMESTAMP DEFAULT NOW()
);

-- Tabela de posts
CREATE TABLE IF NOT EXISTS "Posts" (
    "Id" SERIAL PRIMARY KEY,
    "Title" VARCHAR(200) NOT NULL,
    "Content" TEXT NOT NULL,
    "CreatedAt" TIMESTAMP DEFAULT NOW(),
    "UserId" INTEGER REFERENCES "Users"("Id") ON DELETE CASCADE
);

-- Tabela de planos de usuários
CREATE TABLE IF NOT EXISTS "Plans" (
    "Id" SERIAL PRIMARY KEY,
    "PlanName" VARCHAR(50) NOT NULL UNIQUE
);


-- Tabela de associação entre usuários e planos de usuários
CREATE TABLE IF NOT EXISTS "UserPlans" (
    "UserId" INTEGER NOT NULL REFERENCES "Users"("Id") ON DELETE CASCADE,
    "PlanId" INTEGER NOT NULL REFERENCES "Plans"("Id") ON DELETE CASCADE,
    "AssignedAt" TIMESTAMP DEFAULT NOW(),
    UNIQUE ("UserId", "PlanId") -- Garante que um usuário não possa ter o mesmo plano mais de uma vez
);


INSERT INTO "Plans" ("Id", "PlanName")
VALUES 
    (1, 'Regular'),
    (2, 'Premium');

INSERT INTO "Users" ("Id", "Name", "Email") VALUES
(2563, 'João Silva', 'joao@example.com'),
(4586, 'Maria Oliveira', 'maria@example.com');

INSERT INTO "Posts" ("Id", "Title", "Content", "UserId") VALUES
(2854, 'Primeiro Post', 'Conteúdo do primeiro post', 2563),
(7895, 'Segundo Post', 'Conteúdo do segundo post', 4586);


INSERT INTO "UserPlans" ("UserId", "PlanId")
VALUES 
    (2563, 1), -- Usuário 1 para o plano Regular
    (4586, 2); -- Usuário 2 para o plano Premium