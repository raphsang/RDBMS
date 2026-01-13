# Simple Relational Database Management System (RDBMS)

A lightweight, fully-functional relational database management system built from scratch in Python, with a SQL-like query interface and a web-based demonstration application.

🎯 Project Overview

This project implements a simple but complete RDBMS with the following features:
- Custom storage engine with in-memory operations and disk persistence
- SQL-like query language for database operations
- Indexing system for performance optimization
- Constraint enforcement (PRIMARY KEY, UNIQUE, NOT NULL)
- JOIN operations (INNER JOIN)
- Interactive REPL for command-line database access
- Web application demonstrating practical CRUD operations

 🏗️ Architecture

 Core Components

1. **Database Layer** (`Database` class)
   - Manages multiple tables
   - Handles persistence (serialization/deserialization)
   - Table creation and deletion

2. **Table Layer** (`Table` class)
   - Row storage and management
   - Index management
   - CRUD operations (Create, Read, Update, Delete)
   - Constraint validation

3. **Index Layer** (`Index` class)
   - B-tree-like hash index structure
   - O(1) average-case lookups
   - Automatic maintenance during CRUD operations

4. **Query Layer** (`SQLParser` class)
   - SQL statement parsing
   - Query execution
   - JOIN implementation

5. **Column Schema** (`Column` class)
   - Data type definitions
   - Constraint specification
   - Value validation

## 📊 Supported Features

### Data Types
- `INTEGER` - Whole numbers
- `TEXT` - String values
- `FLOAT` - Floating-point numbers
- `BOOLEAN` - True/False values

### Constraints
- `PRIMARY KEY` - Unique identifier, automatically indexed
- `UNIQUE` - Ensures column values are unique
- `NOT NULL` - Prevents null values

### SQL Operations

#### DDL (Data Definition Language)
```sql
-- Create a table
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER)

-- Drop a table
DROP TABLE users

-- Create an index
CREATE INDEX idx_name ON users (name)

-- Show all tables
SHOW TABLES

-- Describe table structure
DESCRIBE users
```

#### DML (Data Manipulation Language)
```sql
-- Insert data
INSERT INTO users (id, name, age) VALUES (1, 'Alice', 30)

-- Select data
SELECT * FROM users
SELECT name, age FROM users WHERE age > 25

-- Update data
UPDATE users SET age = 31 WHERE id = 1

-- Delete data
DELETE FROM users WHERE id = 1
```

#### Joins
```sql
-- Inner join
SELECT users.name, tasks.title 
FROM users 
INNER JOIN tasks ON users.id = tasks.user_id
```

## 🚀 Quick Start

### 1. REPL Mode (Interactive Console)

```bash
python3 simple_rdbms.py
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

### 2. Web Application

```bash
python3 app.py
```

Then visit: http://127.0.0.1:5000

The web app provides:
- **Task Management** - Create, edit, delete, and toggle tasks
- **User Management** - Manage users with unique constraints
- **SQL Console** - Execute queries directly in the browser
- **Statistics** - View database schema and performance metrics

## 💡 Implementation Details

### Storage Engine

The database uses a hybrid storage approach:
- **In-Memory**: All data is kept in memory for fast access
- **Disk Persistence**: Automatic serialization to disk using Python's pickle
- **Row-Based Storage**: Each row is stored as a dictionary with O(1) access by row ID

### Indexing

Indexes are implemented as hash-based structures:
```python
class Index:
    def __init__(self, column_name: str):
        self.index: Dict[Any, Set[int]] = {}  # value -> set of row_ids
```

- Primary keys are automatically indexed
- Unique constraints automatically create indexes
- Additional indexes can be created manually for performance
- Indexes are maintained automatically during INSERT, UPDATE, DELETE

### Join Implementation

Joins are implemented using a nested loop algorithm:
1. Fetch all rows from both tables
2. For each row in the left table, iterate through right table
3. Check join condition (equality of specified columns)
4. Build result row combining matching columns

### Query Parsing

The SQL parser uses regex-based pattern matching:
- Identifies statement type (SELECT, INSERT, UPDATE, etc.)
- Extracts table names, column lists, and values
- Parses WHERE clauses into filter functions
- Handles JOIN syntax

## 🎓 Educational Value

This project demonstrates:

1. **Database Fundamentals**
   - ACID properties (simplified)
   - Schema design and normalization
   - Index structures and their benefits

2. **Data Structures**
   - Hash tables for indexing
   - Linked structures for row storage
   - Set operations for constraint enforcement

3. **Algorithms**
   - Query optimization through indexing
   - Join algorithms
   - Parsing and compilation

4. **Software Engineering**
   - Object-oriented design
   - Separation of concerns
   - API design

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

## 📝 Key Classes

### Database
Main entry point for database operations.
```python
db = Database("mydb")
db.create_table("users", [Column("id", DataType.INTEGER, primary_key=True)])
```

### Table
Manages rows and operations for a single table.
```python
table = db.get_table("users")
table.insert({"id": 1, "name": "Alice"})
rows = table.select(where=lambda row: row.get("id") > 0)
```

### SQLParser
Parses and executes SQL statements.
```python
result = SQLParser.parse_and_execute(db, "SELECT * FROM users")
```

## 🧪 Example Use Cases

### 1. User Registration System
```python
# Create users table
db.create_table("users", [
    Column("id", DataType.INTEGER, primary_key=True),
    Column("username", DataType.TEXT, unique=True, not_null=True),
    Column("email", DataType.TEXT, unique=True, not_null=True)
])

# Register user
users = db.get_table("users")
users.insert({"id": 1, "username": "alice", "email": "alice@example.com"})
```

### 2. Task Management
```python
# Create tasks table
db.create_table("tasks", [
    Column("id", DataType.INTEGER, primary_key=True),
    Column("user_id", DataType.INTEGER, not_null=True),
    Column("title", DataType.TEXT, not_null=True),
    Column("completed", DataType.BOOLEAN)
])

# Add index for faster user lookups
tasks = db.get_table("tasks")
tasks.create_index("user_id")

# Create task
tasks.insert({"id": 1, "user_id": 1, "title": "Learn SQL", "completed": False})
```

### 3. Querying with Joins
```sql
-- Get all tasks with user information
SELECT users.username, tasks.title, tasks.completed
FROM users
INNER JOIN tasks ON users.id = tasks.user_id
WHERE tasks.completed = 0
```


---

**Note**: This is a simplified RDBMS for educational purposes. For production use, 

please use established databases like PostgreSQL, MySQL, or SQLite.
