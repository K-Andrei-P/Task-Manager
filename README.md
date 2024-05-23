# Task Manager - BETA

#### Description:

My program was made for the purpose of managing a person's days easier. It helps with keeping track of tasks within one's days and displays statistics to the user, showing how the user is doing on which the can then reflect on. The display of statistics also makes doing tasks more gamelike, which helps them avoid procrastination, because it is more fun.

The project was built on the Flask Framework. The project folder contains the necessary:

> **static**

> **templates**

> **app.py**

It also contains the database, containing all the necessary task and user information.

The database _task-manager.db_ has two tables.

> users

which has the collumns:

> "id, username" both unique

and the collumns

> "tasks_created, tasks_completed, email, created_on, hash"

The database also has the table

> tasks

which stores all the information of the tasks that users have created.

The program has 5 path in total, which are all handled differently in _app.py_

The login path "/login" accepts two requests: "GET" and "POST". A "GET" request is sent if it is accessed by link or redirect.

A post request is sent if the user has put in their account username and password. If all the required fields are filled in and the inputted information is correct, the user will then be redirected to the dashboard page, which is the program's homepage.

If a user doesn't have an account yet, a link to the path: "/register" can be clicked, where the user can make a new account. This path accepts two requests: "GET" and "POST". A "POST" request is sent if the user has filled in all the necessary fields, after which the user's information is then stored in the SQL database.

The dashboard path "/" also accepts two requests: "GET" and "POST". When the path is first accessed, the program checks if the user already has a session or is already logged in. If the user is not, they then will be redirected to the login page. Then it checks which request type was asked for.

A post request is only made if the user clicks the checkmark on the daily task to complete it. The status of the completed task with a unique task-id will then be updated in the database and the tasks_completed collumn in the users table will increment by one.

If a "GET" request is made, the program first calculates all the statistics that is to be shown on the dashboard.

This includes the statitics:

> Consistency

> Workload avg: Total tasks until current date / account age

All the calculations are made with the help the datetime, a built in python module.

> Productivity score: consistency _ 100 _ workload_avg

Then all the data for the graph is calculated. For each day of the week, the Completionrate is given. All the necessary information is the extended into the array _data_.

Once all the calculations are made, the function returns the flask function **return template**, where the template: _dashboard.html_ is rendered and all the information is passed through.

The next important path is the "/tasks" path. This path also accepts two request types: "GET" and "POST". The function first handles the case, if the user is logged in or not. It does this by checking if the current user's username is already is in the session, if not the case, they will be redirect to the login page. Once checked, the function checks for the request type.

A "GET" request is made if the user gets redirected to the path or a link to it is clicked.
The program then get all the tasks of the current user and stores it in the variable: _tasks_raw_

All the tasks are then computed and updated to the status: _"ongoing"_ if the status is incorrect. All of this is stored inside the dictionary tasks. Lastly, the function returns the function "render*template" and renders the template: *"tasks.html"\_ and all the necessary information is passed through as well. This template contains Javascript code as well. It is used to display or hide widgets. A widget is displayed if the user creates a new task or clicks on one of the tasks that are listed. Once a task is clicked, the used can then either edit or complete a task. The javascript also turns the status different colours for each different variant.

If a post request is sent, this can mean different things. Firstly, the function checks if the user has edited a function and handles it accordingly.

Then, the function checks if the user has completed a task and updates the database accordingly.

After that, the function checks if the user has searched for a task. If so, the function searches the database for similar names and renders the list of tasks to the user.

For the case, that a user has completed a task but didn't actually finish it, the user can undo their completion by pressing the undo button on the task widget. This then changes the status of the given task accordingly.

Lastly, it checks for the creation of a task. If all the necessary fields are filled in, the new list of tasks will be rerenered to the user.
