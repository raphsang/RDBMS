# Quick Start Guide - Simple RDBMS

## 🚀 Getting Started in 3 Steps

### Step 1: Run the Demo
See all features in action:
```bash
python3 demo.py
```

This demonstrates:
- Table creation with constraints
- INSERT, SELECT, UPDATE, DELETE operations  
- JOIN queries
- Indexing
- Constraint enforcement
- Data persistence

### Step 2: Try the REPL
Interactive SQL console:
```bash
python3 simple_rdbms.py
```

Example commands:
```sql
example_db> CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT NOT NULL, price FLOAT)
example_db> INSERT INTO products (id, name, price) VALUES (1, 'Laptop', 999.99)
example_db> SELECT * FROM products
example_db> exit
```

### Step 3: Launch the Web App
Full-featured task management application:
```bash
python3 app.py
```

Then visit: http://127.0.0.1:5000

The web app includes:
- 📝 Task Management - CRUD operations with JOINs
- 👥 User Management - Unique constraints in action
- 💻 SQL Console - Execute queries in browser
- 📊 Statistics - View database schema and indexes

## 📁 Project Structure

```
simple_rdbms_project/
├── simple_rdbms.py      # Core RDBMS (700+ lines)
├── app.py               # Flask web application
├── demo.py              # Feature demonstration
├── README.md            # Full documentation
├── QUICKSTART.md        # This file
└── templates/           # Web UI templates
    ├── base.html
    ├── index.html       # Tasks page
    ├── users.html
    ├── sql_console.html
    ├── stats.html
    └── edit_task.html
```

## 🎯 Core Features

### Data Types
- INTEGER, TEXT, FLOAT, BOOLEAN

### Constraints  
- PRIMARY KEY (auto-indexed)
- UNIQUE (auto-indexed)
- NOT NULL

### Operations
- CREATE/DROP TABLE
- INSERT, SELECT, UPDATE, DELETE
- INNER JOIN
- CREATE INDEX
- WHERE clauses

### Advanced
- B-tree-like hash indexes
- Automatic constraint enforcement
- Disk persistence (pickle)
- Query parsing and execution

## 💡 Example Workflow

### Creating a Blog Database

```python
from simple_rdbms import Database, Column, DataType, SQLParser

# Create database
db = Database("blog_db")

# Create tables
SQLParser.parse_and_execute(db, 
    "CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL)")

SQLParser.parse_and_execute(db,
    "CREATE TABLE articles (id INTEGER PRIMARY KEY, author_id INTEGER NOT NULL, title TEXT NOT NULL, content TEXT)")

# Insert data
SQLParser.parse_and_execute(db,
    "INSERT INTO authors (id, name) VALUES (1, 'John Doe')")

SQLParser.parse_and_execute(db,
    "INSERT INTO articles (id, author_id, title, content) VALUES (1, 1, 'Hello World', 'My first post')")

# Query with JOIN
result = SQLParser.parse_and_execute(db,
    "SELECT authors.name, articles.title FROM authors INNER JOIN articles ON authors.id = articles.author_id")

print(result)
# Output: [{'authors.name': 'John Doe', 'articles.title': 'Hello World', ...}]
```

## 🔧 Common SQL Commands

### Table Management
```sql
-- Create table
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE)

-- Drop table
DROP TABLE users

-- Show tables
SHOW TABLES

-- Describe table
DESCRIBE users
```

### Data Operations
```sql
-- Insert
INSERT INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')

-- Select all
SELECT * FROM users

-- Select specific columns
SELECT name, email FROM users

-- Select with filter
SELECT * FROM users WHERE id > 5

-- Update
UPDATE users SET email = 'newemail@example.com' WHERE id = 1

-- Delete
DELETE FROM users WHERE id = 1
```

### Joins
```sql
-- Inner join
SELECT users.name, orders.total 
FROM users 
INNER JOIN orders ON users.id = orders.user_id
```

### Indexing
```sql
-- Create index for faster queries
CREATE INDEX idx_email ON users (email)
```

## 🎓 Learning Path

1. **Start with REPL** - Get comfortable with SQL syntax
2. **Run the demo** - See all features working together  
3. **Explore the web app** - See practical CRUD implementation
4. **Read the code** - Understand the internals
5. **Modify and extend** - Add your own features!

## 🐛 Troubleshooting

### Database file locked
Delete the database file:
```bash
rm -rf ./data/*.db
```

### Module not found
Make sure you're in the project directory:
```bash
cd simple_rdbms_project
python3 app.py
```

### Port already in use (web app)
Change the port in app.py:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed from 5000
```
