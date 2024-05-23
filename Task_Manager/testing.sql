-- Creating the users table

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    tasks_created INTEGER NOT NULL,
    tasks_completed INTEGER NOT NULL,
    email TEXT NOT NULL,
    created_on TEXT NOT NULL
);

-- Creating tasks table

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    created_on TEXT NOT NULL,
    starts_on TEXT NOT NULL,
    priority INTEGER NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Creating test task
INSERT INTO tasks (name, user_id, created_on, starts_on, priority, description, status)
VALUES ('My first task', 4, '2015-12-24', '2015-12-26', 5, 'HELLO WORLD', 'pending');

INSERT INTO tasks (name, user_id, created_on, starts_on, priority, description, status)
VALUES ('My Second task', 4, '2015-02-24', '2015-11-26', 5, 'HELLO WORLD', 'completed');

INSERT INTO tasks (name, user_id, created_on, starts_on, priority, description, status)
VALUES ('My Third task', 4, '2015-01-24', '2015-01-26', 5, 'HELLO WORLD', 'ongoing');


-- Creating current test tasks
INSERT INTO tasks (name, user_id, created_on, starts_on, priority, description, status)
VALUES ('A current task', 4, '2015-01-24', '2024-03-31', 3, 'A task that starts on the current date', 'pending');
-- Expected output: status: ongoing

INSERT INTO tasks (name, user_id, created_on, starts_on, priority, description, status)
VALUES ('A before task', 4, '2015-01-24', '2024-03-26', 3, 'A task that starts on the before date', 'pending');
-- expected output: status: ongoing

INSERT INTO tasks (name, user_id, created_on, starts_on, priority, description, status)
VALUES ('A later task', 4, '2015-01-24', '2024-04-04', 3, 'A task that starts on the later date', 'pending');
-- expected output: status: pending