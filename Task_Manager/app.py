from flask import Flask, render_template, request, session, redirect, flash, jsonify, url_for
import json
from sql import SQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'paT6VVMXXU4dGow'
app.config["SESSION_PERMANENT"] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database
db = SQL("task-manager.db")
def to_json(data):
    return json.dumps(data)

# Define the tojson and safe filters
app.jinja_env.filters['tojson'] = to_json

def get_start_of_week(date, start_day=0):
    days_to_subtract = (date.weekday() - start_day) % 7
    start_of_week = date - timedelta(days=days_to_subtract)
    return start_of_week

@app.route('/', methods=['GET', 'POST'])
def index():
    if "username" in session:
        if request.method == "POST":
            # task id is passed through
            db.execute("UPDATE tasks SET status = ? WHERE id = ?", "completed", request.form.get("task_id"))
            db.execute("UPDATE users SET tasks_completed = tasks_completed + ? WHERE id = ?", 1, session["user_id"])
            return redirect("/")
        elif request.method == "GET":
            # Handle Create new Task
            # Handle Editing a Task
            # Data of user

            # Calculating consistency of user:
            # Tasks that are ongoing or completed
            consistencyTasks = db.execute("SELECT * FROM tasks WHERE user_id = ? AND (status = ? OR status = ?)", session["user_id"], "ongoing", "completed")
            
            if consistencyTasks:
                tasks_completed = db.execute("SELECT tasks_completed FROM users WHERE id = ?", session["user_id"])[0]["tasks_completed"]
                
                consistency = int((tasks_completed / len(consistencyTasks)) * 100) if len(consistencyTasks) != 0 else 0
            else:
                consistency = 0
            
            # Calculating workload
            curdate = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            account_date = db.execute("SELECT created_on FROM users WHERE id = ?", session["user_id"])
            if account_date:
                account_created = datetime.strptime(account_date[0]["created_on"], "%Y-%m-%d")
            account_age = (curdate - account_created).days
            if account_age == 0:
                account_age = 1
            tasks_lifetime = len(db.execute("SELECT * FROM tasks WHERE user_id = ? AND (status = ? or status = ?)", session["user_id"], "completed", "ongoing"))

            workload_avg = int(tasks_lifetime / account_age) if account_age != 0 else 0

            # Data for recently added task LIMIT 5
            most_recent = db.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY DATE(created_on) DESC LIMIT 5", session["user_id"])

            # Calculate productivityscore
            productivity_score = consistency * workload_avg

            # DATA FOR THE GRAPH
            # Get the start of the week
            start_of_week = get_start_of_week(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
            raw_data = []

            for i in range(7):
                temp = []
                current_day = start_of_week + timedelta(days=i)
                current_day_str = current_day.strftime('%Y-%m-%d')
                week_day = current_day.strftime("%a")
                temp.append(week_day)
                if current_day > curdate:
                    temp.append(None)
                    raw_data.append(temp)
                    continue
                completed_tasks = db.execute("SELECT * FROM tasks WHERE user_id = ? AND starts_on = ? AND status = ?", session["user_id"], current_day_str, "completed")
                total_tasks = db.execute("SELECT * FROM tasks WHERE user_id = ? AND starts_on = ?", session["user_id"], current_day_str)

                if completed_tasks is not None and total_tasks is not None:
                    amt_completed = len(completed_tasks)
                    amt_total = len(total_tasks)
                    if amt_total > 0:
                        completion_rate = int(amt_completed / amt_total) * 100
                    else:
                        completion_rate = 0
                else:
                    completion_rate = 0

                temp.append(int(completion_rate))
                raw_data.append(temp)

            
            data = [['Day', 'Completionrate']]
            data.extend(raw_data)

            # Data for Daily Task 
            tasks = db.execute("SELECT * FROM tasks WHERE user_id = ? AND starts_on = ?", session["user_id"], curdate.strftime('%Y-%m-%d'))
            daily = {}

            for task in tasks:
                if datetime.strptime(task["starts_on"], "%Y-%m-%d") <= curdate and (task["status"] != "completed" and task["status"] != "ongoing"):
                    db.execute("UPDATE tasks SET status = ? WHERE id = ?", "ongoing", task["id"])
                    task["status"] = "ongoing"
                daily[task["id"]] = {
                    "id": task["id"],
                    "name": task["name"],
                    "created_on": task["created_on"],
                    "starts_on": task["starts_on"],
                    "priority": task["priority"],
                    "description": task["description"],
                    "status": task["status"]
                }
            
            return render_template('dashboard.html', daily=daily, data=data, most_recent=most_recent, consistency=consistency, workload_avg=workload_avg, productivity_score=productivity_score)
    else:
        return redirect('login')
    

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Case: Empty fields
        if not username or not password:
            flash("Please fill in all the required fields!", "fields-required")
            return render_template('login.html')
        
        # Case: User not in database
        user_info = db.execute("SELECT * FROM users WHERE username = ?", username)

        if not user_info:
            flash("Account does not exist", "database-error")
            return render_template('login.html')
        
        # Case: Wrong password
        if not check_password_hash(user_info[0]["hash"], password):
            flash("Wrong username or password", "wrong-info-error")
            return render_template('login.html')
        
        # Put user in session
        session["username"] = username
        session["user_id"] = user_info[0]["id"]
        return redirect('/')
    else:
        return render_template('login.html')

@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        if not username or not email or not password or not confirmation:
            flash("Please fill in all the required fields!", "fields-required")
            return render_template('register.html')
        
        # Case password and confirmation are not the same
        if not password == confirmation:
            flash("Please try again, password and confirmation are not the same!", "fields-required")
            return render_template('register.html')
        
        # All is well, add a new account to database
        curdate = datetime.now()
        date = curdate.strftime("%Y-%m-%d")
        db.execute("INSERT INTO users (username, tasks_created, tasks_completed, email, created_on, hash) VALUES (?, ?, ?, ?, ?, ?)", username, 0, 0, email, date, generate_password_hash(password))
        return redirect('login')
    else:
        return render_template("register.html")
    
@app.route('/tasks', methods=['POST', 'GET'])
def tasks():
    if "username" in session:

        if request.method == 'POST':
            if request.form.get("task_id"):
                # For confirming an edit to a task
                task_id = request.form.get('task_id')
                new_title = request.form.get('title')
                new_start = request.form.get("starts_on")
                new_description = request.form.get("description")
                new_level = request.form.get("level")
                
                # Error Checking
                # Case no task_id:
                if not task_id:
                    flash("Something went wrong.")
                    return redirect('index')

                if new_title:
                    db.execute("UPDATE tasks SET name = ? WHERE id = ?", new_title, task_id)
                
                if new_start:
                    db.execute("UPDATE tasks SET starts_on = ? WHERE id = ?", new_start, task_id)

                if new_description:
                    db.execute("UPDATE tasks SET description = ? WHERE id = ?", new_description, task_id)

                if new_level:
                    db.execute("UPDATE tasks SET priority = ? WHERE id = ?", new_level, task_id)
            elif request.form.get("confirm"):
                # for completing a task
                db.execute("UPDATE tasks SET status = ? WHERE id = ?", "completed", request.form.get("confirm")) 
                db.execute("UPDATE users SET tasks_completed = tasks_completed + ? WHERE id = ?", 1, session["user_id"])
            elif request.form.get("q"):
                search_tasks_raw = db.execute("SELECT * FROM tasks WHERE user_id = ? AND name LIKE ?", session["user_id"], "%"+request.form.get("q")+"%")
                search_tasks = {}
                for task in search_tasks_raw:
                    search_tasks[task["id"]] = {
                        "id": task["id"],
                        "name": task["name"],
                        "created_on": task["created_on"],
                        "starts_on": task["starts_on"],
                        "priority": task["priority"],
                        "description": task["description"],
                        "status": task["status"]
                    }
                return render_template("tasks.html", tasks=search_tasks)
            elif request.form.get("undo"):
                db.execute("UPDATE tasks SET status = ? WHERE id = ?", "ongoing", request.form.get("undo"))
                db.execute("UPDATE users SET tasks_completed = tasks_completed - ? WHERE id = ?", 1, session["user_id"])
            elif request.form.get("create"):
                create_title = request.form.get('title')
                create_start = request.form.get("starts_on")
                create_description = request.form.get("description")
                create_level = request.form.get("level")

                # Error checkig:
                if not create_title or not create_start or not create_level:
                    flash("Please enter all the required fields")
                    return redirect("/tasks")
                
                curdate = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                date = curdate.strftime("%Y-%m-%d")
                if datetime.strptime(create_start, "%Y-%m-%d") <= curdate:
                    status = "ongoing"
                elif datetime.strptime(create_start, "%Y-%m-%d") >= curdate:
                    status = "pending"
                db.execute("INSERT INTO tasks (name, user_id, created_on, starts_on, priority, description, status) VALUES (?, ?, ?, ?, ?, ?, ?)", create_title, session["user_id"], date, create_start, create_level, create_description, status)
                db.execute("UPDATE users SET tasks_created = tasks_created + ? WHERE id = ?", 1, session["user_id"])
                return redirect(url_for("tasks"))


            # Put all tasks from db into a dict
            tasks_raw = db.execute("SELECT * FROM tasks WHERE user_id=?", session["user_id"])
            tasks = {}

            # Get current date for updating the status
            curdate = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            for task in tasks_raw:
                if datetime.strptime(task["starts_on"], "%Y-%m-%d") <= curdate and (task["status"] != "completed" and task["status"] != "ongoing"):
                    db.execute("UPDATE tasks SET status = ? WHERE id = ?", "ongoing", task["id"])
                    task["status"] = "ongoing"
                elif datetime.strptime(task["starts_on"], "%Y-%m-%d") > curdate and task["status"] != "pending":
                    db.execute("UPDATE tasks SET status = ? WHERE id = ?", "pending", task["id"])
                    task["status"] = "pending"
                tasks[task["id"]] = {
                    "id": task["id"],
                    "name": task["name"],
                    "created_on": task["created_on"],
                    "starts_on": task["starts_on"],
                    "priority": task["priority"],
                    "description": task["description"],
                    "status": task["status"]
                }

            return render_template('tasks.html', tasks=tasks)  
        else:
            # If the method is get from link or redirect
            # Put all tasks from db into a dict
            curdate = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tasks_raw = db.execute("SELECT * FROM tasks WHERE user_id=?", session["user_id"])
            tasks = {}
            for task in tasks_raw:
                if datetime.strptime(task["starts_on"], "%Y-%m-%d") <= curdate and (task["status"] != "completed" and task["status"] != "ongoing"):
                    db.execute("UPDATE tasks SET status = ? WHERE id = ?", "ongoing", task["id"])
                    task["status"] = "ongoing"
                
                tasks[task["id"]] = {
                    "id": task["id"],
                    "name": task["name"],
                    "created_on": task["created_on"],
                    "starts_on": task["starts_on"],
                    "priority": task["priority"],
                    "description": task["description"],
                    "status": task["status"]
                }
            return render_template('tasks.html', tasks=tasks)  
    else:
        redirect("/login")

if __name__ == '__main__':
    app.run(debug=True)

