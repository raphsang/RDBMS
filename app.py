"""
Flask Web Application demonstrating the Simple RDBMS
A task management application with CRUD operations
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from simple_rdbms import Database, Column, DataType, SQLParser
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize database
db = Database("webapp_db", storage_path="./db_data")

# Initialize tables if they don't exist
def init_database():
    """Initialize database tables"""
    try:
        # Create users table
        db.create_table("users", [
            Column("id", DataType.INTEGER, primary_key=True),
            Column("username", DataType.TEXT, unique=True, not_null=True),
            Column("email", DataType.TEXT, unique=True, not_null=True),
            Column("created_at", DataType.TEXT)
        ])
        print("Created users table")
    except ValueError:
        print("Users table already exists")
    
    try:
        # Create tasks table
        db.create_table("tasks", [
            Column("id", DataType.INTEGER, primary_key=True),
            Column("user_id", DataType.INTEGER, not_null=True),
            Column("title", DataType.TEXT, not_null=True),
            Column("description", DataType.TEXT),
            Column("completed", DataType.BOOLEAN),
            Column("created_at", DataType.TEXT)
        ])
        
        # Create index on user_id for faster lookups
        tasks_table = db.get_table("tasks")
        tasks_table.create_index("user_id")
        print("Created tasks table")
    except ValueError:
        print("Tasks table already exists")
    
    try:
        # Create categories table
        db.create_table("categories", [
            Column("id", DataType.INTEGER, primary_key=True),
            Column("name", DataType.TEXT, unique=True, not_null=True),
            Column("color", DataType.TEXT)
        ])
        print("Created categories table")
    except ValueError:
        print("Categories table already exists")
    
    try:
        # Create task_categories junction table
        db.create_table("task_categories", [
            Column("task_id", DataType.INTEGER, not_null=True),
            Column("category_id", DataType.INTEGER, not_null=True)
        ])
        print("Created task_categories table")
    except ValueError:
        print("Task_categories table already exists")


# Routes
@app.route('/')
def index():
    """Home page showing all tasks"""
    try:
        # Get all tasks with user information using JOIN
        sql = "SELECT tasks.id, tasks.title, tasks.description, tasks.completed, users.username, tasks.user_id FROM tasks INNER JOIN users ON tasks.user_id = users.id"
        tasks = SQLParser.parse_and_execute(db, sql)
        
        # Get all users for the form
        users = SQLParser.parse_and_execute(db, "SELECT * FROM users")
        
        return render_template('index.html', tasks=tasks, users=users)
    except Exception as e:
        flash(f"Error loading tasks: {str(e)}", "error")
        return render_template('index.html', tasks=[], users=[])


@app.route('/users')
def users():
    """User management page"""
    try:
        users = SQLParser.parse_and_execute(db, "SELECT * FROM users")
        return render_template('users.html', users=users)
    except Exception as e:
        flash(f"Error loading users: {str(e)}", "error")
        return render_template('users.html', users=[])


@app.route('/users/add', methods=['POST'])
def add_user():
    """Add a new user"""
    try:
        username = request.form.get('username')
        email = request.form.get('email')
        
        if not username or not email:
            flash("Username and email are required", "error")
            return redirect(url_for('users'))
        
        # Get next ID
        users_table = db.get_table("users")
        user_id = users_table.next_id
        
        from datetime import datetime
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        sql = f"INSERT INTO users (id, username, email, created_at) VALUES ({user_id}, '{username}', '{email}', '{created_at}')"
        result = SQLParser.parse_and_execute(db, sql)
        
        flash(f"User '{username}' created successfully", "success")
    except Exception as e:
        flash(f"Error creating user: {str(e)}", "error")
    
    return redirect(url_for('users'))


@app.route('/users/delete/<int:user_id>')
def delete_user(user_id):
    """Delete a user"""
    try:
        # First delete all tasks for this user
        SQLParser.parse_and_execute(db, f"DELETE FROM tasks WHERE user_id = {user_id}")
        
        # Then delete the user
        sql = f"DELETE FROM users WHERE id = {user_id}"
        result = SQLParser.parse_and_execute(db, sql)
        
        flash("User deleted successfully", "success")
    except Exception as e:
        flash(f"Error deleting user: {str(e)}", "error")
    
    return redirect(url_for('users'))


@app.route('/tasks/add', methods=['POST'])
def add_task():
    """Add a new task"""
    try:
        user_id = request.form.get('user_id')
        title = request.form.get('title')
        description = request.form.get('description', '')
        
        if not user_id or not title:
            flash("User and title are required", "error")
            return redirect(url_for('index'))
        
        # Get next ID
        tasks_table = db.get_table("tasks")
        task_id = tasks_table.next_id
        
        from datetime import datetime
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        sql = f"INSERT INTO tasks (id, user_id, title, description, completed, created_at) VALUES ({task_id}, {user_id}, '{title}', '{description}', 0, '{created_at}')"
        result = SQLParser.parse_and_execute(db, sql)
        
        flash("Task created successfully", "success")
    except Exception as e:
        flash(f"Error creating task: {str(e)}", "error")
    
    return redirect(url_for('index'))


@app.route('/tasks/toggle/<int:task_id>')
def toggle_task(task_id):
    """Toggle task completion status"""
    try:
        # Get current task
        tasks_table = db.get_table("tasks")
        task_results = tasks_table.select(where=lambda row: row.get('id') == task_id)
        
        if not task_results:
            flash("Task not found", "error")
            return redirect(url_for('index'))
        
        current_status = task_results[0].get('completed', False)
        new_status = 0 if current_status else 1
        
        sql = f"UPDATE tasks SET completed = {new_status} WHERE id = {task_id}"
        result = SQLParser.parse_and_execute(db, sql)
        
        flash("Task status updated", "success")
    except Exception as e:
        flash(f"Error updating task: {str(e)}", "error")
    
    return redirect(url_for('index'))


@app.route('/tasks/delete/<int:task_id>')
def delete_task(task_id):
    """Delete a task"""
    try:
        sql = f"DELETE FROM tasks WHERE id = {task_id}"
        result = SQLParser.parse_and_execute(db, sql)
        
        flash("Task deleted successfully", "success")
    except Exception as e:
        flash(f"Error deleting task: {str(e)}", "error")
    
    return redirect(url_for('index'))


@app.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    """Edit a task"""
    tasks_table = db.get_table("tasks")
    
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            description = request.form.get('description', '')
            
            if not title:
                flash("Title is required", "error")
                return redirect(url_for('edit_task', task_id=task_id))
            
            sql = f"UPDATE tasks SET title = '{title}', description = '{description}' WHERE id = {task_id}"
            result = SQLParser.parse_and_execute(db, sql)
            
            flash("Task updated successfully", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error updating task: {str(e)}", "error")
    
    # GET request - show edit form
    try:
        task_results = tasks_table.select(where=lambda row: row.get('id') == task_id)
        
        if not task_results:
            flash("Task not found", "error")
            return redirect(url_for('index'))
        
        task = task_results[0]
        return render_template('edit_task.html', task=task)
    except Exception as e:
        flash(f"Error loading task: {str(e)}", "error")
        return redirect(url_for('index'))


@app.route('/sql')
def sql_console():
    """SQL console page"""
    return render_template('sql_console.html')


@app.route('/sql/execute', methods=['POST'])
def execute_sql():
    """Execute SQL query"""
    try:
        sql = request.form.get('sql', '').strip()
        
        if not sql:
            return jsonify({"error": "No SQL provided"})
        
        result = SQLParser.parse_and_execute(db, sql)
        
        if isinstance(result, list):
            return jsonify({"success": True, "data": result, "type": "table"})
        else:
            return jsonify({"success": True, "message": str(result), "type": "message"})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/stats')
def stats():
    """Database statistics page"""
    try:
        stats_data = {
            "tables": []
        }
        
        for table_name, table in db.tables.items():
            table_info = {
                "name": table_name,
                "row_count": len(table.rows),
                "columns": [str(col) for col in table.columns.values()],
                "indexes": list(table.indexes.keys()),
                "primary_key": table.primary_key
            }
            stats_data["tables"].append(table_info)
        
        return render_template('stats.html', stats=stats_data)
    except Exception as e:
        flash(f"Error loading stats: {str(e)}", "error")
        return render_template('stats.html', stats={"tables": []})


if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Add some sample data if tables are empty
    try:
        users_table = db.get_table("users")
        if len(users_table.rows) == 0:
            from datetime import datetime
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add sample users
            SQLParser.parse_and_execute(db, f"INSERT INTO users (id, username, email, created_at) VALUES (1, 'alice', 'alice@example.com', '{created_at}')")
            SQLParser.parse_and_execute(db, f"INSERT INTO users (id, username, email, created_at) VALUES (2, 'bob', 'bob@example.com', '{created_at}')")
            
            # Add sample tasks
            SQLParser.parse_and_execute(db, f"INSERT INTO tasks (id, user_id, title, description, completed, created_at) VALUES (1, 1, 'Learn RDBMS concepts', 'Study database fundamentals', 1, '{created_at}')")
            SQLParser.parse_and_execute(db, f"INSERT INTO tasks (id, user_id, title, description, completed, created_at) VALUES (2, 1, 'Build simple database', 'Implement basic CRUD operations', 0, '{created_at}')")
            SQLParser.parse_and_execute(db, f"INSERT INTO tasks (id, user_id, title, description, completed, created_at) VALUES (3, 2, 'Write documentation', 'Document the RDBMS API', 0, '{created_at}')")
            
            print("Added sample data")
    except Exception as e:
        print(f"Sample data already exists or error: {e}")
    
    print("\n" + "="*60)
    print("Simple RDBMS Web Application")
    print("="*60)
    print("\nStarting Flask server...")
    print("Visit: http://127.0.0.1:5000")
    print("\nAvailable routes:")
    print("  / - Task management")
    print("  /users - User management")
    print("  /sql - SQL console")
    print("  /stats - Database statistics")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)