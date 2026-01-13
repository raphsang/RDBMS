"""
Simple Relational Database Management System (RDBMS)
Supports: table creation, CRUD operations, indexing, constraints, and joins
"""

import json
import os
import pickle
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
import re


class DataType(Enum):
    """Supported column data types"""
    INTEGER = "INTEGER"
    TEXT = "TEXT"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"


class Column:
    """Represents a table column with type and constraints"""
    def __init__(self, name: str, data_type: DataType, 
                 primary_key: bool = False, unique: bool = False,
                 not_null: bool = False):
        self.name = name
        self.data_type = data_type
        self.primary_key = primary_key
        self.unique = unique
        self.not_null = not_null or primary_key  # Primary keys are always NOT NULL

    def validate(self, value: Any) -> Any:
        """Validate and convert value to appropriate type"""
        if value is None:
            if self.not_null:
                raise ValueError(f"Column '{self.name}' cannot be NULL")
            return None
        
        if self.data_type == DataType.INTEGER:
            return int(value)
        elif self.data_type == DataType.TEXT:
            return str(value)
        elif self.data_type == DataType.FLOAT:
            return float(value)
        elif self.data_type == DataType.BOOLEAN:
            if isinstance(value, bool):
                return value
            return str(value).lower() in ('true', '1', 'yes')
        
        return value

    def __repr__(self):
        constraints = []
        if self.primary_key:
            constraints.append("PRIMARY KEY")
        if self.unique:
            constraints.append("UNIQUE")
        if self.not_null:
            constraints.append("NOT NULL")
        
        constraint_str = " " + " ".join(constraints) if constraints else ""
        return f"{self.name} {self.data_type.value}{constraint_str}"


class Index:
    """B-tree-like index for faster lookups"""
    def __init__(self, column_name: str):
        self.column_name = column_name
        self.index: Dict[Any, Set[int]] = {}  # value -> set of row_ids
    
    def add(self, value: Any, row_id: int):
        """Add a value to the index"""
        if value not in self.index:
            self.index[value] = set()
        self.index[value].add(row_id)
    
    def remove(self, value: Any, row_id: int):
        """Remove a value from the index"""
        if value in self.index:
            self.index[value].discard(row_id)
            if not self.index[value]:
                del self.index[value]
    
    def find(self, value: Any) -> Set[int]:
        """Find all row_ids with the given value"""
        return self.index.get(value, set())
    
    def clear(self):
        """Clear the entire index"""
        self.index.clear()


class Table:
    """Represents a database table with rows and indexes"""
    def __init__(self, name: str, columns: List[Column]):
        self.name = name
        self.columns = {col.name: col for col in columns}
        self.column_order = [col.name for col in columns]
        self.rows: Dict[int, Dict[str, Any]] = {}  # row_id -> row_data
        self.next_id = 1
        self.indexes: Dict[str, Index] = {}
        
        # Find primary key
        self.primary_key = None
        for col in columns:
            if col.primary_key:
                if self.primary_key:
                    raise ValueError("Table can only have one primary key")
                self.primary_key = col.name
                self.create_index(col.name)  # Auto-index primary key
        
        # Auto-index unique columns
        for col in columns:
            if col.unique:
                self.create_index(col.name)
    
    def create_index(self, column_name: str):
        """Create an index on a column"""
        if column_name not in self.columns:
            raise ValueError(f"Column '{column_name}' does not exist")
        
        if column_name in self.indexes:
            return  # Index already exists
        
        index = Index(column_name)
        # Build index from existing data
        for row_id, row in self.rows.items():
            value = row.get(column_name)
            if value is not None:
                index.add(value, row_id)
        
        self.indexes[column_name] = index
    
    def insert(self, values: Dict[str, Any]) -> int:
        """Insert a new row into the table"""
        # Validate all columns
        row_data = {}
        for col_name, col in self.columns.items():
            value = values.get(col_name)
            validated_value = col.validate(value)
            row_data[col_name] = validated_value
            
            # Check unique constraint
            if validated_value is not None and (col.unique or col.primary_key):
                if col_name in self.indexes:
                    existing = self.indexes[col_name].find(validated_value)
                    if existing:
                        raise ValueError(f"Duplicate value '{validated_value}' for {col_name}")
        
        row_id = self.next_id
        self.next_id += 1
        self.rows[row_id] = row_data
        
        # Update indexes
        for col_name, index in self.indexes.items():
            value = row_data.get(col_name)
            if value is not None:
                index.add(value, row_id)
        
        return row_id
    
    def select(self, columns: Optional[List[str]] = None, 
               where: Optional[callable] = None) -> List[Dict[str, Any]]:
        """Select rows from the table"""
        if columns is None:
            columns = self.column_order
        
        results = []
        for row_id, row in self.rows.items():
            if where is None or where(row):
                result_row = {col: row.get(col) for col in columns}
                result_row['_row_id'] = row_id  # Include internal ID
                results.append(result_row)
        
        return results
    
    def update(self, values: Dict[str, Any], where: Optional[callable] = None) -> int:
        """Update rows in the table"""
        updated_count = 0
        
        for row_id, row in list(self.rows.items()):
            if where is None or where(row):
                # Remove old values from indexes
                for col_name, index in self.indexes.items():
                    old_value = row.get(col_name)
                    if old_value is not None:
                        index.remove(old_value, row_id)
                
                # Update values
                for col_name, value in values.items():
                    if col_name not in self.columns:
                        raise ValueError(f"Column '{col_name}' does not exist")
                    
                    validated_value = self.columns[col_name].validate(value)
                    
                    # Check unique constraint
                    col = self.columns[col_name]
                    if validated_value is not None and (col.unique or col.primary_key):
                        if col_name in self.indexes:
                            existing = self.indexes[col_name].find(validated_value)
                            # Allow update if the only existing row is this one
                            if existing and existing != {row_id}:
                                raise ValueError(f"Duplicate value '{validated_value}' for {col_name}")
                    
                    row[col_name] = validated_value
                
                # Add new values to indexes
                for col_name, index in self.indexes.items():
                    new_value = row.get(col_name)
                    if new_value is not None:
                        index.add(new_value, row_id)
                
                updated_count += 1
        
        return updated_count
    
    def delete(self, where: Optional[callable] = None) -> int:
        """Delete rows from the table"""
        deleted_count = 0
        
        for row_id, row in list(self.rows.items()):
            if where is None or where(row):
                # Remove from indexes
                for col_name, index in self.indexes.items():
                    value = row.get(col_name)
                    if value is not None:
                        index.remove(value, row_id)
                
                del self.rows[row_id]
                deleted_count += 1
        
        return deleted_count
    
    def __repr__(self):
        return f"Table({self.name}, columns={list(self.columns.keys())})"


class Database:
    """Main database class managing tables and persistence"""
    def __init__(self, name: str, storage_path: str = "./data"):
        self.name = name
        self.storage_path = storage_path
        self.tables: Dict[str, Table] = {}
        self.db_file = os.path.join(storage_path, f"{name}.db")
        
        # Create storage directory
        os.makedirs(storage_path, exist_ok=True)
        
        # Load existing database if it exists
        if os.path.exists(self.db_file):
            self.load()
    
    def create_table(self, name: str, columns: List[Column]) -> Table:
        """Create a new table"""
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists")
        
        table = Table(name, columns)
        self.tables[name] = table
        self.save()
        return table
    
    def drop_table(self, name: str):
        """Drop a table"""
        if name not in self.tables:
            raise ValueError(f"Table '{name}' does not exist")
        
        del self.tables[name]
        self.save()
    
    def get_table(self, name: str) -> Table:
        """Get a table by name"""
        if name not in self.tables:
            raise ValueError(f"Table '{name}' does not exist")
        return self.tables[name]
    
    def save(self):
        """Persist database to disk"""
        os.makedirs(self.storage_path, exist_ok=True)
        with open(self.db_file, 'wb') as f:
            pickle.dump(self, f)
    
    def load(self):
        """Load database from disk"""
        with open(self.db_file, 'rb') as f:
            loaded_db = pickle.load(f)
            self.tables = loaded_db.tables
    
    def __repr__(self):
        return f"Database({self.name}, tables={list(self.tables.keys())})"


class SQLParser:
    """Simple SQL parser for basic queries"""
    
    @staticmethod
    def parse_and_execute(db: Database, sql: str) -> Any:
        """Parse and execute SQL statement"""
        sql = sql.strip().rstrip(';')
        
        # CREATE TABLE
        if sql.upper().startswith('CREATE TABLE'):
            return SQLParser._parse_create_table(db, sql)
        
        # DROP TABLE
        elif sql.upper().startswith('DROP TABLE'):
            return SQLParser._parse_drop_table(db, sql)
        
        # INSERT
        elif sql.upper().startswith('INSERT INTO'):
            return SQLParser._parse_insert(db, sql)
        
        # SELECT
        elif sql.upper().startswith('SELECT'):
            return SQLParser._parse_select(db, sql)
        
        # UPDATE
        elif sql.upper().startswith('UPDATE'):
            return SQLParser._parse_update(db, sql)
        
        # DELETE
        elif sql.upper().startswith('DELETE FROM'):
            return SQLParser._parse_delete(db, sql)
        
        # CREATE INDEX
        elif sql.upper().startswith('CREATE INDEX'):
            return SQLParser._parse_create_index(db, sql)
        
        # SHOW TABLES
        elif sql.upper().startswith('SHOW TABLES'):
            return list(db.tables.keys())
        
        # DESCRIBE
        elif sql.upper().startswith('DESCRIBE') or sql.upper().startswith('DESC'):
            return SQLParser._parse_describe(db, sql)
        
        else:
            raise ValueError(f"Unsupported SQL statement: {sql}")
    
    @staticmethod
    def _parse_create_table(db: Database, sql: str):
        """Parse CREATE TABLE statement"""
        # Example: CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER)
        match = re.match(r'CREATE TABLE\s+(\w+)\s*\((.*)\)', sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid CREATE TABLE syntax")
        
        table_name = match.group(1)
        columns_str = match.group(2)
        
        columns = []
        for col_def in columns_str.split(','):
            col_def = col_def.strip()
            parts = col_def.split()
            
            if len(parts) < 2:
                raise ValueError(f"Invalid column definition: {col_def}")
            
            col_name = parts[0]
            col_type = DataType[parts[1].upper()]
            
            primary_key = 'PRIMARY' in col_def.upper() and 'KEY' in col_def.upper()
            unique = 'UNIQUE' in col_def.upper()
            not_null = 'NOT' in col_def.upper() and 'NULL' in col_def.upper()
            
            columns.append(Column(col_name, col_type, primary_key, unique, not_null))
        
        db.create_table(table_name, columns)
        return f"Table '{table_name}' created successfully"
    
    @staticmethod
    def _parse_drop_table(db: Database, sql: str):
        """Parse DROP TABLE statement"""
        match = re.match(r'DROP TABLE\s+(\w+)', sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DROP TABLE syntax")
        
        table_name = match.group(1)
        db.drop_table(table_name)
        return f"Table '{table_name}' dropped successfully"
    
    @staticmethod
    def _parse_insert(db: Database, sql: str):
        """Parse INSERT statement"""
        # Example: INSERT INTO users (id, name, age) VALUES (1, 'John', 25)
        match = re.match(r'INSERT INTO\s+(\w+)\s*\((.*?)\)\s*VALUES\s*\((.*?)\)', sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid INSERT syntax")
        
        table_name = match.group(1)
        columns = [c.strip() for c in match.group(2).split(',')]
        values = [v.strip().strip("'\"") for v in match.group(3).split(',')]
        
        if len(columns) != len(values):
            raise ValueError("Column count doesn't match value count")
        
        table = db.get_table(table_name)
        values_dict = dict(zip(columns, values))
        row_id = table.insert(values_dict)
        
        db.save()
        return f"1 row inserted (row_id: {row_id})"
    
    @staticmethod
    def _parse_select(db: Database, sql: str):
        """Parse SELECT statement with JOIN support"""
        # Simple SELECT: SELECT * FROM users
        # SELECT with WHERE: SELECT name, age FROM users WHERE age > 18
        # SELECT with JOIN: SELECT users.name, orders.total FROM users INNER JOIN orders ON users.id = orders.user_id
        
        # Check for JOIN
        if 'JOIN' in sql.upper():
            return SQLParser._parse_select_with_join(db, sql)
        
        # Parse simple SELECT
        match = re.match(r'SELECT\s+(.*?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+))?', sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid SELECT syntax")
        
        columns_str = match.group(1).strip()
        table_name = match.group(2)
        where_clause = match.group(3)
        
        table = db.get_table(table_name)
        
        if columns_str == '*':
            columns = None
        else:
            columns = [c.strip() for c in columns_str.split(',')]
        
        where_func = None
        if where_clause:
            where_func = SQLParser._parse_where_clause(where_clause)
        
        results = table.select(columns, where_func)
        return results
    
    @staticmethod
    def _parse_select_with_join(db: Database, sql: str):
        """Parse SELECT with INNER JOIN"""
        # Example: SELECT users.name, orders.total FROM users INNER JOIN orders ON users.id = orders.user_id
        pattern = r'SELECT\s+(.*?)\s+FROM\s+(\w+)\s+INNER\s+JOIN\s+(\w+)\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)'
        match = re.match(pattern, sql, re.IGNORECASE)
        
        if not match:
            raise ValueError("Invalid JOIN syntax")
        
        columns_str = match.group(1).strip()
        left_table_name = match.group(2)
        right_table_name = match.group(3)
        join_left_table = match.group(4)
        join_left_col = match.group(5)
        join_right_table = match.group(6)
        join_right_col = match.group(7)
        
        left_table = db.get_table(left_table_name)
        right_table = db.get_table(right_table_name)
        
        # Parse columns
        if columns_str == '*':
            columns = [(left_table_name, col) for col in left_table.column_order] + \
                     [(right_table_name, col) for col in right_table.column_order]
        else:
            columns = []
            for col_spec in columns_str.split(','):
                col_spec = col_spec.strip()
                if '.' in col_spec:
                    table, col = col_spec.split('.')
                    columns.append((table.strip(), col.strip()))
                else:
                    columns.append((left_table_name, col_spec))
        
        # Perform join
        left_rows = left_table.select()
        right_rows = right_table.select()
        
        results = []
        for left_row in left_rows:
            for right_row in right_rows:
                # Check join condition
                left_val = left_row.get(join_left_col) if join_left_table == left_table_name else right_row.get(join_left_col)
                right_val = right_row.get(join_right_col) if join_right_table == right_table_name else left_row.get(join_right_col)
                
                if left_val == right_val:
                    # Build result row
                    result = {}
                    for table_name, col_name in columns:
                        if table_name == left_table_name:
                            result[f"{table_name}.{col_name}"] = left_row.get(col_name)
                        else:
                            result[f"{table_name}.{col_name}"] = right_row.get(col_name)
                    results.append(result)
        
        return results
    
    @staticmethod
    def _parse_update(db: Database, sql: str):
        """Parse UPDATE statement"""
        # Example: UPDATE users SET age = 26 WHERE id = 1
        # Use non-greedy matching and explicit WHERE boundary
        match = re.match(r'UPDATE\s+(\w+)\s+SET\s+(.+?)(?:\s+WHERE\s+(.+))?$', sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid UPDATE syntax")
        
        table_name = match.group(1)
        set_clause = match.group(2)
        where_clause = match.group(3)
        
        table = db.get_table(table_name)
        
        # Parse SET clause
        values = {}
        for assignment in set_clause.split(','):
            parts = assignment.split('=')
            if len(parts) != 2:
                raise ValueError(f"Invalid SET clause: {assignment}")
            col, val = parts[0].strip(), parts[1].strip()
            values[col] = val.strip("'\"")
        
        where_func = None
        if where_clause:
            where_func = SQLParser._parse_where_clause(where_clause)
        
        count = table.update(values, where_func)
        db.save()
        return f"{count} row(s) updated"
    
    @staticmethod
    def _parse_delete(db: Database, sql: str):
        """Parse DELETE statement"""
        # Example: DELETE FROM users WHERE id = 1
        match = re.match(r'DELETE FROM\s+(\w+)(?:\s+WHERE\s+(.+))?', sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DELETE syntax")
        
        table_name = match.group(1)
        where_clause = match.group(2)
        
        table = db.get_table(table_name)
        
        where_func = None
        if where_clause:
            where_func = SQLParser._parse_where_clause(where_clause)
        
        count = table.delete(where_func)
        db.save()
        return f"{count} row(s) deleted"
    
    @staticmethod
    def _parse_create_index(db: Database, sql: str):
        """Parse CREATE INDEX statement"""
        # Example: CREATE INDEX idx_name ON users (name)
        match = re.match(r'CREATE INDEX\s+\w+\s+ON\s+(\w+)\s*\((.*?)\)', sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid CREATE INDEX syntax")
        
        table_name = match.group(1)
        column_name = match.group(2).strip()
        
        table = db.get_table(table_name)
        table.create_index(column_name)
        db.save()
        return f"Index created on {table_name}.{column_name}"
    
    @staticmethod
    def _parse_describe(db: Database, sql: str):
        """Parse DESCRIBE statement"""
        match = re.match(r'(?:DESCRIBE|DESC)\s+(\w+)', sql, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DESCRIBE syntax")
        
        table_name = match.group(1)
        table = db.get_table(table_name)
        
        return [str(col) for col in table.columns.values()]
    
    @staticmethod
    def _parse_where_clause(where_clause: str) -> callable:
        """Parse WHERE clause and return a filter function"""
        # Simple implementation for basic comparisons
        # Supports: column = value, column > value, column < value, etc.
        
        operators = {
            '=': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
        }
        
        for op, func in operators.items():
            if op in where_clause:
                parts = where_clause.split(op)
                if len(parts) == 2:
                    col_name = parts[0].strip()
                    value = parts[1].strip().strip("'\"")
                    
                    # Try to convert value to appropriate type
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                    
                    return lambda row: func(row.get(col_name), value)
        
        raise ValueError(f"Unsupported WHERE clause: {where_clause}")


class REPL:
    """Interactive REPL for the database"""
    def __init__(self, db: Database):
        self.db = db
    
    def start(self):
        """Start the REPL"""
        print(f"Simple RDBMS - Database: {self.db.name}")
        print("Type 'help' for commands, 'exit' to quit\n")
        
        while True:
            try:
                sql = input(f"{self.db.name}> ").strip()
                
                if not sql:
                    continue
                
                if sql.lower() == 'exit' or sql.lower() == 'quit':
                    print("Goodbye!")
                    break
                
                if sql.lower() == 'help':
                    self._show_help()
                    continue
                
                result = SQLParser.parse_and_execute(self.db, sql)
                
                if isinstance(result, list):
                    if len(result) > 0:
                        if isinstance(result[0], dict):
                            # Table results
                            self._print_table(result)
                        else:
                            # Simple list
                            for item in result:
                                print(item)
                    else:
                        print("0 rows returned")
                else:
                    print(result)
                
                print()
            
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Error: {str(e)}\n")
    
    def _print_table(self, results: List[Dict[str, Any]]):
        """Pretty print table results"""
        if not results:
            return
        
        # Get all columns
        columns = list(results[0].keys())
        
        # Calculate column widths
        widths = {col: len(str(col)) for col in columns}
        for row in results:
            for col in columns:
                widths[col] = max(widths[col], len(str(row.get(col, ''))))
        
        # Print header
        header = " | ".join(str(col).ljust(widths[col]) for col in columns)
        print(header)
        print("-" * len(header))
        
        # Print rows
        for row in results:
            print(" | ".join(str(row.get(col, '')).ljust(widths[col]) for col in columns))
        
        print(f"\n{len(results)} row(s) returned")
    
    def _show_help(self):
        """Show help information"""
        help_text = """
Available Commands:
  CREATE TABLE <name> (<columns>)  - Create a new table
  DROP TABLE <name>                - Drop a table
  INSERT INTO <table> (...) VALUES (...)  - Insert a row
  SELECT <cols> FROM <table> [WHERE ...]  - Select rows
  UPDATE <table> SET ... [WHERE ...]      - Update rows
  DELETE FROM <table> [WHERE ...]         - Delete rows
  CREATE INDEX <name> ON <table> (<col>)  - Create an index
  SHOW TABLES                      - List all tables
  DESCRIBE <table>                 - Show table structure
  
Examples:
  CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER)
  INSERT INTO users (id, name, age) VALUES (1, 'John', 25)
  SELECT * FROM users WHERE age > 20
  UPDATE users SET age = 26 WHERE id = 1
  DELETE FROM users WHERE id = 1
  SELECT users.name, orders.total FROM users INNER JOIN orders ON users.id = orders.user_id
"""
        print(help_text)


if __name__ == "__main__":
    # Example usage
    db = Database("example_db")
    repl = REPL(db)
    repl.start()