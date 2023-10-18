from flask import Flask, render_template, request, redirect, send_from_directory
import mysql.connector as ms
app = Flask(__name__, static_folder='templates/static')
from datetime import datetime
from flask import jsonify, request
now = datetime.now()
current_time = now.strftime("%Y-%m-%d %H:%M:%S")
# Simulated user database (Repla    ce with an actual database in a real application)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/')
def mdfycr():
    return render_template('modify_car.html')
@app.route('/process_option1', methods=['POST'])
def process_option1():
    option = request.json.get('option')  # Get the 'option' from the JSON payload
    if option == 'MONTHLY':
        print('mon')
    elif option == 'DAILY':
        print('dail')
    elif option == 'YEARLY':
        print('yearl')
    return jsonify({'message': 'Option received successfully'})
@app.route('/modify_car', methods=['POST', 'GET'])
def modify_car():
    if request.method == 'POST':
        car_number = request.form.get('car_number')
        btnpr = request.form.get('btnpr')
        if btnpr == 'delete_car':
            ab = ms.connect(host='localhost', username='root', password='dpsbn', database='cars')
            cursor = ab.cursor()

            # First, select the car to be deleted
            nmm='SELECT * FROM car_no WHERE car_number=%s'
            cursor.execute(nmm,(car_number,))
            car_info = cursor.fetchall()
            if car_info:
                cursor.execute('DELETE FROM car_no WHERE car_number=%s', (car_number,))
                ab.commit()  
                message = f"Deleted car with number: {car_number}"
            else:
                message = f"Car with number {car_number} does not exist"
            cursor.close()
            ab.close()
        elif btnpr == 'add_car':
            ab = ms.connect(host='localhost', username='root', password='dpsbn', database='cars')
            cursor = ab.cursor()
            nmm='SELECT * FROM car_no WHERE car_number=%s'
            cursor.execute(nmm,(car_number,))
            car_info = cursor.fetchall()
            if car_info:
                message = f"Car with the Number {car_number} already Exists"
            else:
                message = f"Car with number {car_number} does not exist"
                cursor.execute('INSERT INTO car_no (car_number,timestamp) values (%s,%s)', (car_number,current_time))
                ab.commit()  
                message = f"Added car with number: {car_number}"
            cursor.close()
            ab.close()
        return render_template('modify_car.html', message=message)  # Pass the message to the template
    return mdfycr()
@app.route('/add_user', methods=['POST', 'GET'])
def add_user():
    global message
    message = None  # Initialize message

    added_username = None  # Initialize added_username

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin_status = request.form.get('admin_status')
        
        db = ms.connect(host='localhost', user='root', passwd='dpsbn', database='cars')
        cursor = db.cursor()
        cursor.execute('SELECT * FROM pswd')
        existing_users = cursor.fetchall()
        
        for user in existing_users:
            if username == user[1]:
                message = f"User {username} already exists"
                return render_template('add_user.html', added_username=None, message=message)  # Return early

        try:
            cursor.execute('INSERT INTO pswd (username, password, admin) VALUES (%s, %s, %s)',
                        (username, password, admin_status))
            db.commit()
            added_username = username
            message = f"Successfully added user: {username}"
        except ms.IntegrityError as e:
            # Handle the IntegrityError (Duplicate entry error)
            message = f"The user {username} already exists in the database."

        cursor.close()
        db.close()
        
    return render_template('add_user.html', added_username=added_username, message=message)
@app.route('/remove_user', methods=['POST', 'GET'])
def remove_user():
    global message
    message = None  # Initialize message

    removed_username = None  # Initialize removed_username

    if request.method == 'POST':
        username = request.form.get('username').strip()  # Remove leading/trailing spaces
        
        db = ms.connect(host='localhost', user='root', passwd='dpsbn', database='cars')
        cursor = db.cursor()
        cursor.execute('SELECT * FROM pswd')
        existing_users = cursor.fetchall()
        
        user_found = False
        for user in existing_users:
            if username == user[0]:  # Case-insensitive comparison
                user_found = True
                cursor.execute('DELETE FROM pswd WHERE username=%s', (user[0],))  # Use the actual username from the database
                db.commit()
                removed_username = user[0]
                message = f"Successfully removed user: {user[0]}"
                break
        
        if not user_found:
            message = f"The user {username} does not exist in the database."

        cursor.close()
        db.close()
        
    return render_template('remove_user.html', removed_username=removed_username, message=message)
@app.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    global message
    message = None  # Initialize message
    message_type = None  # Initialize message_type

    if request.method == 'POST':
        username = request.form.get('username')
        new_password = request.form.get('new_password')
        
        db = ms.connect(host='localhost', user='root', passwd='dpsbn', database='cars')
        cursor = db.cursor()
        cursor.execute('SELECT * FROM pswd')
        existing_users = cursor.fetchall()
        
        user_found = False
        for user in existing_users:
            if username == user[0]:
                user_found = True
                cursor.execute('UPDATE pswd SET password=%s WHERE username=%s', (new_password, username))
                db.commit()
                message = f"Password reset successful for user: {username}"
                message_type = 'success'
                break
        
        if not user_found:
            message = f"The user {username} does not exist in the database."
            message_type = 'error'

        cursor.close()
        db.close()
        
    return render_template('reset_password.html', message=message, message_type=message_type)
@app.route('/rep_home')
def rep_home():
    process_option1
    return render_template('rep_home.html')
@app.route('/admin_home')
def admin_home():
    return render_template('admin_home.html')
@app.route('/login')
def login_page():
    return render_template('login.html')
@app.route('/process_option', methods=['POST'])
@app.route('/mdfy')
def mdfy_mode():
    return redirect('/modify_car')
@app.route('/user_mod_page')
def user_mod_page():
    return render_template('user_mod.html')
@app.route('/add_user_page')
def add_user_page():
    return render_template('add_user.html')
@app.route('/process_option', methods=['POST'])
@app.route('/process_option', methods=['POST'])
def process_option():
    option = request.json.get('option')  # Get the 'option' from the JSON payload
    if option == 'MDFY':
        return redirect('/modify_car_page')
    elif option == 'ARU':
        return 'Hello World'
    return render_template('admin_home.html')  # Return the template with no specific option
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    db = ms.connect(host='localhost', user='root', passwd='dpsbn', database='cars')
    cursor = db.cursor()
    cursor.execute('select * from pswd')
    a = cursor.fetchall()
    for i in a:
        if username == i[0] and password == i[1]:
            if i[2] == 'Yes':  
                return render_template('admin_home.html')
            elif i[2] == 'No':  
                return 'Login Successful'
    
    message = 'Invalid credentials. Please try again'
    return render_template('login.html', message=message)

@app.route('/static/')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(debug=True)
