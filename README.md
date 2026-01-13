# Simple Relational Database Management System (RDBMS)

A lightweight, fully-functional relational database management system built from scratch in Python, with a SQL-like query interface and a web-based demonstration application.

---

## 🎯 Project Overview

This project implements a simple but complete RDBMS with the following features:

- Custom storage engine with in-memory operations and disk persistence
- SQL-like query language for database operations
- Indexing system for performance optimization
- Constraint enforcement (PRIMARY KEY, UNIQUE, NOT NULL)
- JOIN operations (INNER JOIN)
- Interactive REPL for command-line database access
- Web application demonstrating practical CRUD operations

---

## 🛠️ Setup Instructions

Follow these steps to run the project locally:

### 1. Clone the repository
```bash
git clone https://github.com/raphsang/RDBMS.git
cd RDBMS/simple_rdbms_project
````

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the web application

```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

### 6. Optional: REPL Mode (Interactive Console)

```bash
python simple_rdbms.py
```

Example session:

```sql
example_db> CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL)
Table 'users' created successfully

example_db> INSERT INTO users (id, name) VALUES (1, 'Alice')
1 row inserted (row_id: 1)

example_db> SELECT * FROM users
id | name  
----------
1  | Alice 

1 row(s) returned

example_db> exit
Goodbye!
```

---

## 📄 Requirements

Install these exact versions to avoid compatibility issues:

```text
Flask==3.1.2
Werkzeug==3.1.5
Jinja2==3.1.6
click==8.3.1
colorama==0.4.6
itsdangerous==2.2.0
blinker==1.9.0
MarkupSafe==3.0.3
```

Save this as `requirements.txt` in the root of `simple_rdbms_project`.

---

## 🏗️ Architecture

### Core Components

1. **Database Layer** (`Database` class)

   * Manages multiple tables
   * Handles persistence (serialization/deserialization)
   * Table creation and deletion

2. **Table Layer** (`Table` class)

   * Row storage and management
   * Index management
   * CRUD operations (Create, Read, Update, Delete)
   * Constraint validation

3. **Index Layer** (`Index` class)

   * Hash-based index structure
   * O(1) average-case lookups
   * Automatic maintenance during CRUD operations

4. **Query Layer** (`SQLParser` class)

   * SQL statement parsing
   * Query execution
   * JOIN implementation

5. **Column Schema** (`Column` class)

   * Data type definitions
   * Constraint specification
   * Value validation

---

## 📊 Supported Features

### Data Types

* `INTEGER` - Whole numbers
* `TEXT` - String values
* `FLOAT` - Floating-point numbers
* `BOOLEAN` - True/False values

### Constraints

* `PRIMARY KEY` - Unique identifier, automatically indexed
* `UNIQUE` - Ensures column values are unique
* `NOT NULL` - Prevents null values

### SQL Operations

#### DDL (Data Definition Language)

```sql
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER)
DROP TABLE users
CREATE INDEX idx_name ON users (name)
SHOW TABLES
DESCRIBE users
```

#### DML (Data Manipulation Language)

```sql
INSERT INTO users (id, name, age) VALUES (1, 'Alice', 30)
SELECT * FROM users
SELECT name, age FROM users WHERE age > 25
UPDATE users SET age = 31 WHERE id = 1
DELETE FROM users WHERE id = 1
```

#### Joins

```sql
SELECT users.name, tasks.title 
FROM users 
INNER JOIN tasks ON users.id = tasks.user_id
```

---

## 🔧 Code Structure

```
simple_rdbms_project/
├── simple_rdbms.py          # Core RDBMS implementation
├── app.py                   # Flask web application
├── templates/               # HTML templates
│   ├── base.html           # Base template with styling
│   ├── index.html          # Task management page
│   ├── users.html          # User management page
│   ├── sql_console.html    # SQL query interface
│   ├── stats.html          # Database statistics
│   └── edit_task.html      # Task editing form
├── db_data/                # Database storage directory
│   └── webapp_db.db        # Persisted database file
└── README.md               # This file
```

---

## 💡 Implementation Details

* **Storage Engine:** In-memory + disk persistence via pickle
* **Indexes:** Hash-based, automatic maintenance, supports PRIMARY KEY & UNIQUE
* **Joins:** Nested-loop implementation
* **Query Parsing:** Regex-based, supports SELECT, INSERT, UPDATE, DELETE

---

## 🎓 Educational Value

Demonstrates database fundamentals, data structures, algorithms, and software engineering principles such as:

* ACID (simplified)
* Hash tables and sets
* Query optimization
* Object-oriented design and separation of concerns

---

## 🧪 Example Use Cases

### User Registration System

```python
db.create_table("users", [
    Column("id", DataType.INTEGER, primary_key=True),
    Column("username", DataType.TEXT, unique=True, not_null=True),
    Column("email", DataType.TEXT, unique=True, not_null=True)
])
users = db.get_table("users")
users.insert({"id": 1, "username": "alice", "email": "alice@example.com"})
```

### Task Management

```python
db.create_table("tasks", [
    Column("id", DataType.INTEGER, primary_key=True),
    Column("user_id", DataType.INTEGER, not_null=True),
    Column("title", DataType.TEXT, not_null=True),
    Column("completed", DataType.BOOLEAN)
])
tasks = db.get_table("tasks")
tasks.create_index("user_id")
tasks.insert({"id": 1, "user_id": 1, "title": "Learn SQL", "completed": False})
```

### Querying with Joins

```sql
SELECT users.username, tasks.title, tasks.completed
FROM users
INNER JOIN tasks ON users.id = tasks.user_id
WHERE tasks.completed = 0
```
