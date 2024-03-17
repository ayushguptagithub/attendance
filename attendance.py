
from flask import Flask, render_template, request, flash, jsonify, url_for,redirect,session
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from datetime import date as d
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import jsonify
import json
import base64
import os

app = Flask(__name__, static_url_path='/static')
app.secret_key="Ayush@2041"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # Use 465 for secure connections
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'checkin12390@gmail.com'
app.config['MAIL_PASSWORD'] = 'dtvtxofktnxijekn'
app.config['MAIL_DEFAULT_SENDER'] = 'checkin12390@example.com'

# Configure MySQL
app.config['MYSQL_HOST'] = 'b9exja7aekbltqudbv2z-mysql.services.clever-cloud.com'
app.config['MYSQL_USER'] = 'uqpxcxl9bnhhj5dk'
app.config['MYSQL_PASSWORD'] = 'uqpxcxl9bnhhj5dk'
app.config['MYSQL_DB'] = 'b9exja7aekbltqudbv2z'

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'root'
# app.config['MYSQL_DB'] = 'attendance'

# Initialize Flask-Mail
mail = Mail(app)
mysql = MySQL(app)


def get_user_by_email(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    return user




@app.route('/signin.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT usertype, email, name, status FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
        cur.close()



        if user:    
            if user[3]!="Approved":
                flash('Your account is not yet approved by the Admin,if you have recently signup kindly wait until admin approves your account','danger')
                return redirect(url_for('login')) 
            else:
                session['usertype'] = user[0]
                session['email'] = user[1]
                session['name'] = user[2]
                
                return redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('signin.html')

    

from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

serializer = URLSafeTimedSerializer(app.secret_key)

@app.route('/forgot_password.html', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')

        user = get_user_by_email(email)
        if user:
            # Generate a unique token for the user with a 10-minute expiration time
            expiration_time = datetime.utcnow() + timedelta(minutes=10)
            token = serializer.dumps({'email': email, 'exp': expiration_time.timestamp()}, salt='password-reset')

            reset_link = url_for('change_password', token=token, _external=True)
            send_password_reset_email(email, reset_link)

            flash("Password reset link has been sent to your email.")
            return redirect(url_for('forgot_password'))

        flash("User not found", "error")

    return render_template('forgot_password.html')


def send_password_reset_email(email, reset_link):
    alert_message = ""
    subject = 'Password Reset Request'
    body = f'Click the following link to reset your password: {reset_link}'

    msg = Message(subject, recipients=[email], body=body)
    
    try:
        mail.send(msg)
        alert_message = "An email has been sent to you with instructions"
    except Exception as e:
        alert_message = f"Error sending email: {str(e)}"
    return alert_message



@app.route('/change_password/<token>', methods=['GET', 'POST'])
def change_password(token):
    alert_message = ""

    try:
        # Load the token and check if it's still valid
        data = serializer.loads(token, salt='password-reset', max_age=600)  # 10 minutes (in seconds)
        email = data.get('email')

        if request.method == 'POST':
            password = request.form['password']
            confirmpassword = request.form['confirmpassword']

            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET password=%s, confirmpassword=%s WHERE email=%s",
                        (password, confirmpassword, email))
            mysql.connection.commit()
            cur.close()

            if cur.rowcount > 0:
                alert_message = 'Password Changed'
                return redirect(url_for('login'))
            else:
                alert_message = "Can't Change Password"

    except Exception as e:
        alert_message = f"Invalid or expired token: {str(e)}"

    return render_template('change_password.html', alert_message=alert_message)

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session
    session.clear()
   
    # Return a response, if needed
    return render_template('signin.html')


app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images')
@app.route('/signup.html', methods=['POST', 'GET'])
def user_register():
    alert_message = None

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM classes")
    class_list = cur.fetchall()

    if request.method == 'POST':
        # Extract form data
        usertype = "student"
        batch_id = request.form['batch_id']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        phone = request.form['phone']
        classes = request.form['class_id']
        
        # Handle photo upload
        if 'photo' not in request.files:
            flash('No file part')
            return redirect(request.url)
        photo = request.files['photo']
        
        # If the user does not select a file, the browser submits an empty part without filename
        if photo.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        # Save the photo with a filename based on student's name and email
        # Example: "John_Doe_johndoe@example.com.jpg"
        filename = secure_filename(f"{name}_{email}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{photo.filename.split('.')[-1]}")
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(photo_path)

        # Check if the email is already in the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()
        cur.close()

        if existing_user:
            # Email is not unique; handle the situation (set alert message)
            alert_message = 'Email already exists. Please choose a different email.'
            return render_template('signup.html', alert_message=alert_message)

        # Insert the user into the database with the photo path
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (usertype, name, email, phone, password, confirmpassword, classes, photo_path,batch) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)", 
                    (usertype, name, email, phone, password, confirmpassword, classes, filename,batch_id))
        mysql.connection.commit()
        cur.close()

        # Set success message and redirect to login
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    # If request method is GET, simply render the signup page
    return render_template('signup.html', alert_message=alert_message,class_list=class_list)

@app.route('/', methods=['GET', 'POST'])
def index():
    usertype = None
    name = None
    email = None
    user_data = None
    subject_list = None
    
    if 'usertype' in session and 'email' in session and 'name' in session:
        usertype = session['usertype']
        email = session['email']
        name = session['name']

        cur = mysql.connection.cursor()
        query = "SELECT * FROM users WHERE email = %s"
        cur.execute(query, (email,))
        user_data = cur.fetchone()

        # Fetch subjects based on batch_id associated with the logged-in user
        cur = mysql.connection.cursor()
        subject_query = "SELECT * FROM subject WHERE batch_id = (SELECT batch FROM users WHERE email = %s)"
        cur.execute(subject_query, (email,))
        subject_list = cur.fetchall()

        cur = mysql.connection.cursor()
        query = """
            SELECT (SELECT COUNT(lecture_id) FROM attendance  WHERE student_id = (SELECT student_id FROM student WHERE user_id = (SELECT id FROM users WHERE email = %s))  AND status = 'present') AS total_attended,  (SELECT COUNT(lecture_id) FROM attendance  WHERE student_id = (SELECT student_id FROM student WHERE user_id = (SELECT id FROM users WHERE email = 'rushikesh@gmail.com')) AND status = 'absent') AS total_absent;
        """
        cur.execute(query, (email,))
        total_present = cur.fetchone()

        cur = mysql.connection.cursor()
        query = """
             SELECT count(lecture_id) FROM attendance WHERE student_id = (SELECT student_id FROM student WHERE user_id =(select id from users where email = %s) ) ;

        """
        cur.execute(query, (email,))
        total_lectures = cur.fetchone()



        # Fetch lecture count for each subject
        lecture_count = []
        for subject in subject_list:
            cur.execute("SELECT count(lecture_id) FROM lecture WHERE subject_id = %s", (subject[0],))
            lecture_count.append(cur.fetchone()[0])
        print(lecture_count)
        

    else:
        return redirect(url_for('login'))
    
    return render_template('index.html', usertype=usertype, email=email, name=name, user_data=user_data, subject_list=subject_list, lecture_count=lecture_count,total_lectures=total_lectures,total_present=total_present)
@app.route('/lectures.html/<int:subject_id>', methods=['GET', 'POST'])
def lecture(subject_id):
    usertype = None
    name = None
    email = None
    user_data = None
    lecture_list = None
    attendance_status = None  # Added variable to hold attendance status
    
    if 'usertype' in session and 'email' in session and 'name' in session:
        usertype = session['usertype']
        email = session['email']
        name = session['name']

        cur = mysql.connection.cursor()
        query = "SELECT * FROM users WHERE email = %s"
        cur.execute(query, (email,))
        user_data = cur.fetchone()

        # Fetch lectures based on subject_id
        cur.execute("SELECT * FROM lecture WHERE subject_id = %s", (subject_id,))
        lecture_list = cur.fetchall()

        cur.execute("SELECT student_id FROM student WHERE user_id = (SELECT id FROM users WHERE email = %s)", (email,))
        student_id = cur.fetchone()[0]
        today_date_str = datetime.now().strftime("%Y-%m-%d")
        # Fetch attendance status for each lecture dynamically
        attendance_status = []
        for lecture in lecture_list:
            cur.execute("SELECT status FROM attendance WHERE lecture_id = %s AND student_id = %s", (lecture[0], student_id))
            status = cur.fetchone()
            attendance_status.append(status[0] if status else None)

        # Fetch lecture count for the subject
        lecture_count = len(lecture_list)

    else:
        return redirect(url_for('login'))
    
    return render_template('lectures.html', usertype=usertype, email=email, name=name, user_data=user_data, lecture_list=lecture_list, lecture_count=lecture_count, subject_id=subject_id, attendance_status=attendance_status,student_id=student_id,today_date_str=today_date_str)

@app.route('/view_attendance.html/<int:lecture_id>')
def view_attendance(lecture_id):
    usertype = None
    name = None
    email = None
    
    
    if 'usertype' in session and 'email' in session and 'name' in session:
        usertype = session['usertype']
        email = session['email']
        name = session['name']

        cur = mysql.connection.cursor()
        query = "SELECT * FROM users WHERE email = %s"
        cur.execute(query, (email,))
        user_data = cur.fetchone()

        cur = mysql.connection.cursor()
        query = "SELECT student_name, status,lecture.lecture_date FROM attendance, student,lecture WHERE attendance.lecture_id = %s AND student.student_id = attendance.student_id AND lecture.lecture_id = attendance.lecture_id"
        cur.execute(query, (lecture_id,))
        attendance_data = cur.fetchall()
        print(attendance_data)


    return render_template('view_attendance.html', usertype=usertype, email=email, name=name, user_data=user_data,attendance_data=attendance_data)



import cv2
from pyzbar.pyzbar import decode

@app.route('/lectures.html/<int:subject_id>/<int:lecture_id>/<int:student_id>')
def scan_qr_code(subject_id,lecture_id, student_id):
    # Open camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return "Error: Unable to access the camera."

    qr_code_detected = False

    while not qr_code_detected:
        # Read frame from camera
        ret, frame = cap.read()

        if not ret:
            print("Error: Unable to capture frame.")
            break

        # Decode QR codes
        decoded_objects = decode(frame)

        # Display the frame
        cv2.imshow('QR Code Scanner', frame)

        # Check for QR codes in the frame
        if decoded_objects:
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                # print('Scanned QR Code:', qr_data)

                cur = mysql.connection.cursor()
                query = "SELECT g_qr_data FROM attendance WHERE lecture_id = %s and student_id=%s"
                cur.execute(query, (lecture_id, student_id,))
                g_qr_data = cur.fetchone()
                
                if qr_data == g_qr_data[0]:  # Access the first element of the tuple
                    # Update the database
                    cur = mysql.connection.cursor()
                    query = "UPDATE attendance SET m_qr_data = %s, status = %s WHERE lecture_id = %s AND student_id = %s"
                    cur.execute(query, (qr_data, "present", lecture_id, student_id))
                    mysql.connection.commit()  # Commit changes to the database
                    qr_code_detected = True  # Set flag to True to exit the loop
                    break  # Exit the loop after detecting a QR code

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Check if the window is closed
        if cv2.getWindowProperty('QR Code Scanner', cv2.WND_PROP_VISIBLE) < 1:
            break


    # Release the camera and close OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
    return redirect(url_for('lecture', subject_id=subject_id))




@app.route('/profile.html', methods=['POST','GET'])
def edit_profile():
    usertype = None
    name = None
    email = None
    user_data = None
    
    if 'usertype' in session and 'email' in session and 'name' in session:
        usertype = session['usertype']
        email = session['email']
        name = session['name']

        cur = mysql.connection.cursor()
        query = "SELECT * FROM users WHERE email = %s"
        cur.execute(query, (email,))
        user_data = cur.fetchone()

        if request.method == 'POST':
            name = request.form['name']
            phone = request.form['phone']
            classes = request.form['classes']
            
            # Handle photo upload
            if 'photo' not in request.files:
                flash('No file part')
                return redirect(request.url)
            photo = request.files['photo']
            
            # If the user does not select a file, the browser submits an empty part without filename
            if photo.filename == '':
                flash('No selected file')
                return redirect(request.url)
            
            # Save the photo with a filename based on student's name and email
            # Example: "John_Doe_johndoe@example.com.jpg"
            filename = secure_filename(f"{name}_{email}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{photo.filename.split('.')[-1]}")
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)

            # Update the user in the database with the new information and photo path
            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET name = %s, phone = %s, classes = %s, photo_path = %s WHERE email = %s", 
                        (name ,phone, classes, filename, email))
            mysql.connection.commit()
            cur.close()

            # Set success message and redirect to profile page
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('edit_profile'))

    else:
        return redirect(url_for('login'))
    
    return render_template('profile.html', usertype=usertype, email=email, name=name, user_data=user_data)



@app.route('/add_colleges.html', methods=['POST','GET'])
def add_colleges():
    usertype = None
    name = None
    email = None
    user_data = None
    
    if 'usertype' in session and 'email' in session and 'name' in session:
        usertype = session['usertype']
        email = session['email']
        name = session['name']

        cur = mysql.connection.cursor()
        query = "SELECT * FROM users WHERE email = %s"
        cur.execute(query, (email,))
        user_data = cur.fetchone()

        cur = mysql.connection.cursor()
        cur.execute("select * from classes")
        class_list=cur.fetchall()

        if request.method == 'POST':
            name = request.form['name']

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO classes (class_name) VALUES (%s)", 
                        (name,))
            mysql.connection.commit()
            cur.close()
            

            # Set success message and redirect to profile page
            flash('Classes\College added successfully!', 'success')
            return redirect(url_for('add_colleges'))

    else:
        return redirect(url_for('login'))
    
    return render_template('add_colleges.html', usertype=usertype, email=email, name=name, user_data=user_data, class_list=class_list)

@app.route('/deleteClass/<int:id>', methods=['POST', 'GET'])
def delete_class(id):
    cur = mysql.connection.cursor()
    query = "DELETE FROM classes WHERE class_id = %s"
    cur.execute(query, (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('add_colleges'))

@app.route('/deleteStudent/<int:id>', methods=['POST', 'GET'])
def delete_student(id):
    cur = mysql.connection.cursor()
    query = "DELETE FROM student WHERE user_id = %s"
    cur.execute(query, (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('approve_students'))

@app.route('/update_class', methods=['POST'])
def update_class():
    data = request.get_json()
    class_id = data.get('id')
    new_name = data.get('new_name')

    cur = mysql.connection.cursor()
    query = "UPDATE classes SET class_name = %s WHERE class_id = %s"
    cur.execute(query, (new_name, class_id))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Class updated successfully'})
    


@app.route('/add_batch.html', methods=['POST','GET'])
def add_batch():
    usertype = None
    name = None
    email = None
    user_data = None
    
    if 'usertype' in session and 'email' in session and 'name' in session:
        usertype = session['usertype']
        email = session['email']
        name = session['name']

        cur = mysql.connection.cursor()
        query = "SELECT * FROM users WHERE email = %s"
        cur.execute(query, (email,))
        user_data = cur.fetchone()

        classes = "SELECT batch_id, classes.class_name, batch_name FROM batch,classes where batch.class_id=classes.class_id"
        cur.execute(classes)
        class_list = cur.fetchall()

        if request.method == 'POST':
            batch = request.form['batch']
            class_id = request.form['class_id']

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO batch (class_id,batch_name) VALUES (%s,%s)", 
                        (class_id,batch,))
            mysql.connection.commit()
            cur.close()

            # Set success message and redirect to profile page
            flash('Batch added successfully!', 'success')
            return redirect(url_for('add_colleges'))

    else:
        return redirect(url_for('login'))
    
    return render_template('add_batch.html', usertype=usertype, email=email, name=name, user_data=user_data,class_list=class_list)


@app.route('/add_subject.html', methods=['POST', 'GET'])
def add_subject():
    usertype = None
    name = None
    email = None
    user_data = None
    class_list = None
    batch_list = None

    if 'usertype' in session and 'email' in session and 'name' in session:
        usertype = session['usertype']
        email = session['email']
        name = session['name']

        cur = mysql.connection.cursor()
        query = "SELECT * FROM users WHERE email = %s"
        cur.execute(query, (email,))
        user_data = cur.fetchone()

        cur.execute("SELECT * FROM classes")
        class_list = cur.fetchall()

        classes = "SELECT classes.class_name,batch.batch_name,subject.subject_name from subject,batch,classes where batch.batch_id =subject.batch_id and batch.class_id = classes.class_id;"
        cur.execute(classes)
        subject_list = cur.fetchall()

        if request.method == 'POST':
            class_id = request.form['class_id']
            batch_id = request.form['batch_id']  # Retrieve the selected batch ID from the form
            subject_name = request.form['subject_name']

            cur.execute("INSERT INTO subject ( batch_id, subject_name) VALUES ( %s, %s)",
                        ( batch_id, subject_name))
            mysql.connection.commit()
            cur.close()

            flash('Subject added successfully!', 'success')
            return redirect(url_for('add_subject'))

    else:
        return redirect(url_for('login'))

    return render_template('add_subject.html', usertype=usertype, email=email, name=name, user_data=user_data, class_list=class_list, batch_list=batch_list or [],subject_list=subject_list)


@app.route('/get_batches')
def get_batches():
    class_id = request.args.get('class_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT batch_id, batch_name FROM batch WHERE class_id = %s", (class_id,))
    batches = cur.fetchall()
    cur.close()
    return jsonify(batches)

@app.route('/get_subjects')
def get_subjects():
    batch_id = request.args.get('batch_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT subject_id, subject_name FROM subject WHERE batch_id = %s", (batch_id,))
    subjects = cur.fetchall()
    cur.close()
    return jsonify(subjects)

@app.route('/get_lecture')
def get_lecture():
    subject_id = request.args.get('subject_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT lecture_id, lecture_date FROM lecture WHERE subject_id = %s", (subject_id,))
    lecture = cur.fetchall()
    cur.close()
    return jsonify(lecture)

@app.route('/add_lecture.html', methods=['GET', 'POST'])
def add_lecture():
    usertype = None
    name = None
    email = None
    user_data = None

    if 'usertype' in session and 'email' in session and 'name' in session:
        usertype = session['usertype']
        email = session['email']
        name = session['name']

        cur = mysql.connection.cursor()
        query = "SELECT * FROM users WHERE email = %s"
        cur.execute(query, (email,))
        user_data = cur.fetchone()

        cur.execute("SELECT * FROM classes")
        class_list = cur.fetchall()

        
        classes = "SELECT classes.class_name,batch.batch_name,subject.subject_name,lecture.lecture_date,lecture.lecture_topic,lecture_time,lecture.hour from subject,batch,classes,lecture where batch.batch_id =subject.batch_id and batch.class_id = classes.class_id and lecture.subject_id = subject.subject_id;"
        cur.execute(classes)
        subject_list = cur.fetchall()

        if request.method == 'POST':
            class_id = request.form['class_id']
            batch_id = request.form['batch_id']
            subject_id = request.form['subject_id']
            lecture_date = request.form['lecture_date']
            lecture_topic = request.form['lecture_topic']
            lecture_time = request.form['lecture_time']
            hour = request.form['hour']

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO lecture (subject_id, lecture_date, lecture_topic, lecture_time,hour) VALUES (%s, %s, %s, %s, %s)",
                        (subject_id, lecture_date, lecture_topic, lecture_time, hour))
            mysql.connection.commit()
            cur.close()
            flash('Lecture added successfully!','success')
            return redirect(url_for('add_lecture'))

        return render_template('add_lecture.html', usertype=usertype, email=email, name=name, user_data=user_data,class_list=class_list,subject_list=subject_list)
    else:
        return redirect(url_for('login'))

import qrcode
from flask import request, redirect, url_for, render_template, flash, jsonify
from datetime import datetime, timedelta
import random

@app.route('/generate_qr_code.html', methods=['GET', 'POST'])
def generate_qr_code():
    usertype = None
    name = None
    email = None
    user_data = None
    class_list = None

    if 'usertype' in session and 'email' in session and 'name' in session:
        usertype = session['usertype']
        email = session['email']
        name = session['name']

        cur = mysql.connection.cursor()
        query = "SELECT * FROM users WHERE email = %s"
        cur.execute(query, (email,))
        user_data = cur.fetchone()

        cur.execute("SELECT * FROM classes")
        class_list = cur.fetchall()

        if request.method == 'POST':
            class_id = request.form['class_id']
            batch_id = request.form['batch_id']
            subject_id_str = request.form['subject_id']
            lecture_id = request.form['lecture_id']
            student_id = int(subject_id_str)

            # Fetch lecture data from the database
            cur.execute("SELECT lecture_date FROM lecture WHERE lecture_id = %s", (lecture_id,))
            lecture_data = cur.fetchone()
            if lecture_data:
                lecture_date = lecture_data[0]
            else:
                # Handle case where lecture with the specified ID is not found
                lecture_date = None

            # If lecture_date is found, proceed with inserting into attendance table
            if lecture_date:
                lecture_data = ""

                # Fetch student_id based on class_id and batch_id
                cur.execute("SELECT student_id FROM student WHERE class_id = %s AND batch_id = %s", (class_id, batch_id))
                student_data = cur.fetchall()
                
                # Fetch existing student_ids for the specified lecture_id from the attendance table
                cur.execute("SELECT student_id FROM attendance WHERE lecture_id = %s", (lecture_id,))
                existing_students = [row[0] for row in cur.fetchall()]
                
                for student_id_row in student_data:
                    student_id = student_id_row[0]
                    # Check if the student_id already exists for the specified lecture_id
                    if student_id not in existing_students:
                        cur.execute("""INSERT INTO attendance (lecture_id, student_id, status, g_qr_data) 
                                VALUES (%s, %s, %s, %s)""", (lecture_id, student_id, 'absent', lecture_data))
                        mysql.connection.commit()
                    else:
                        # Skip the student if already exists
                        continue

                return redirect(url_for('g_qr_code', lecture_id=lecture_id, date=lecture_date))
                
    return render_template('generate_qr_code.html', usertype=usertype, email=email, name=name, user_data=user_data, class_list=class_list)


from flask import Flask, render_template_string
import qrcode
import io
import base64
import random

def generate_qr_data(lecture_id, date):
    lecture_data = f"Lecture ID: {lecture_id}\nDate: {date}\nRandom Number: {random.randint(1000, 9999)}"
    cur = mysql.connection.cursor()
    query = "UPDATE attendance SET g_qr_data = %s WHERE lecture_id = %s and status=%s"
    cur.execute(query, (lecture_data, lecture_id,'absent'))
    mysql.connection.commit()  
    cur.close()
    return lecture_data
@app.route('/update_attendance/<int:lecture_id>', methods=['GET','POST'])
def update_attendance(lecture_id):
    cur = mysql.connection.cursor()
    query = "UPDATE attendance SET g_qr_data = '' WHERE lecture_id = %s and status = 'absent'"
    cur.execute(query, (lecture_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('generate_qr_code'))

@app.route('/g_qr_code/<int:lecture_id>/<string:date>')
def g_qr_code(lecture_id, date):
    lecture_data = generate_qr_data(lecture_id, date)

    # Generate QR code
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(lecture_data)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert image to base64 string
    buffered = io.BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return render_template_string(
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>QR Code for Lecture</title>
            <style>
            /* CSS styles */
             .modal {
    display: flex;
    align-items: center; /* Vertically center the modal */
    justify-content: center; /* Horizontally center the modal */
    overflow: auto; /* Enable scrolling if content exceeds modal height */
}

.modal-dialog {
    max-width: 800px; /* Adjust maximum width of the modal dialog */
}

.modal-content {
    border-radius: 10px; /* Apply border radius to the modal content */
    box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.1); /* Add shadow to the modal content */
}

.modal-header {
    background-color: #007bff; /* Header background color */
    color: #fff; /* Header text color */
    border-radius: 10px 10px 0 0; /* Apply border radius to the header */
}

.modal-title {
    font-weight: bold; /* Make modal title bold */
}

.modal-body {
    padding: 20px; /* Add padding to the modal body */
}

.modal-footer {
    background-color: #f7f7f7; /* Footer background color */
    border-top: none; /* Remove border from the top */
    border-radius: 0 0 10px 10px; /* Apply border radius to the footer */
}

.btn {
    display: inline-block;
    margin-left: auto; 
    margin-right: auto;
    padding: 12px 24px; /* Adjust padding as needed */
    background-color: #007bff; /* Button background color */
    color: #fff; /* Button text color */
    border: none; /* Remove button border */
    border-radius: 4px; /* Apply border radius */
    cursor: pointer; /* Change cursor to pointer on hover */
    transition: background-color 0.3s ease; /* Add transition for smooth hover effect */
}

.btn:hover {
    background-color: #0056b3; /* Change background color on hover */
}
            </style>
        </head>
        <body>
            <div class="modal fade" id="qrCodeModal" tabindex="-1" aria-labelledby="qrCodeModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="qrCodeModalLabel">QR Code for Lecture Attendance</h5>
                        </div>
                        <div class="modal-body text-center">
                            <img id="qrCodeImg" src="data:image/png;base64,{{ qr_code }}" alt="QR Code">
                        </div>
                        <div class="modal-footer">
                            <a href="{{url_for('update_attendance',lecture_id=lecture_id) }}" class="btn btn-sm btn-primary text-white">Close</a>
                        </div>
                    </div>
                </div>
            </div>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        

        </body>
        </html>
        """,
        qr_code=img_str,
        lecture_id=lecture_id
    )



@app.route('/qr_code')
def qr_code():
    lecture_data = generate_qr_data()

    # Generate QR code
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(lecture_data)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert image to base64 string
    buffered = io.BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return img_str



@app.route('/approve_students.html', methods=['GET', 'POST'])
def approve_students():
    usertype = None
    name = None
    email = None
    user_data = None

    if 'usertype' in session and 'email' in session and 'name' in session:
        usertype = session['usertype']
        email = session['email']
        name = session['name']

        cur = mysql.connection.cursor()
        query = "SELECT * FROM users WHERE email = %s"
        cur.execute(query, (email,))
        user_data = cur.fetchone()

        cur = mysql.connection.cursor()
        query = "SELECT id,photo_path,name,email,phone,classes,batch FROM users WHERE status IS NULL"
        cur.execute(query)
        students_list = cur.fetchall()

        cur = mysql.connection.cursor()
        query = " select student.student_id , users.photo_path ,student.student_name ,email,phone,classes.class_name ,batch.batch_name from student,users,classes , batch where student.user_id=users.id and batch.batch_id = student.batch_id and classes.class_id = student.class_id"
        cur.execute(query)
        students_list_approved = cur.fetchall()


        return render_template('approve_students.html', usertype=usertype, email=email, name=name, user_data=user_data,students_list = students_list ,students_list_approved=students_list_approved)
    else:
        return redirect(url_for('login'))


@app.route('/approve_student/<int:student_id>', methods=['POST'])
def approve_student(student_id):
    if 'usertype' in session and session['usertype'] == 'admin':
        cur = mysql.connection.cursor()

        # Update the user's status to "Approved"
        update_query = "UPDATE users SET status = 'Approved' WHERE id = %s"
        cur.execute(update_query, (student_id,))
        mysql.connection.commit()

        # Insert data into the student table
        select_query = "SELECT * FROM users WHERE id = %s"
        cur.execute(select_query, (student_id,))
        student_data = cur.fetchone()

        insert_query = "INSERT INTO student (user_id, batch_id, student_name, class_id) VALUES (%s, %s, %s, %s)"
        cur.execute(insert_query, (student_data[0], student_data[10], student_data[2], student_data[9]))
        mysql.connection.commit()

        flash('Student approved and data inserted successfully!', 'success')
        return redirect(url_for('approve_students'))
    else:
        flash('You are not authorized to perform this action.', 'danger')
        return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)



