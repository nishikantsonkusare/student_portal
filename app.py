from flask import Flask, redirect, render_template, url_for, session, request, flash, send_from_directory, send_file
import os
import xlrd
from flask_mysqldb import MySQL
from datetime import datetime
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from PIL import Image

UPLOAD_FOLDER = os.getcwd() + '\static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
PDF_ALLOWED_EXTENSIONS = {'pdf'}
XLS_ALLOWED_EXTENSIONS = {'xls'}

app = Flask(__name__)
bcrypt = Bcrypt(app)
mysql = MySQL(app)
app.secret_key = "adjljadlnohohohaou7917391639gboadlnlal"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'student'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.route('/', methods = ['GET','POST'])
def home():

    if 'user' in session:
        return redirect("/dashboard")

    elif request.method == 'POST':
        name = request.form['user']
        upass = request.form['pass']

        if name == 'administrator' and upass == 'administrator':
            return render_template('admin/new_faculty_add.html')
        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT mob FROM users WHERE mob = %s",(name,))
            data = cur.fetchall()
            if data:
                cur.execute("SELECT id, name, mob, pass, user_type, profile_img FROM users WHERE mob = %s",(name,))
                user_data = cur.fetchall()
                cur.close()
                if bcrypt.check_password_hash(user_data[0][3], upass):
                    session['id'] = user_data[0][0]
                    session['name'] = user_data[0][1]
                    session['user'] = user_data[0][2]
                    session['user_type'] = user_data[0][4]
                    session['img'] = user_data[0][5]
                    
                    if session['user_type'] == 'admin':
                        return redirect('/dashboard')
                    else:
                        return redirect('/dashboard')
                else:
                    flash(f'Please enter correct password.')
                    return redirect("/")
            else:
                flash(f"Please enter valid username.")
                return redirect("/")
            
    else:
        return render_template("login.html")

@app.route("/dashboard", methods = ['GET','POST'])
def dashboard():
    if request.method == 'POST':
        title = request.form['title']
        des = request.form['des']
        branch = request.form['branch']
        year = request.form['year']
        section = request.form['section']
        today = datetime.now().date()

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO note(title,des,branch, year, section, date) VALUES (%s,%s,%s,%s,%s,%s)", (title,des,branch,year,section,today))
        mysql.connection.commit()
        cur.close()
        flash(f'Notification generated successfully.')
        return redirect("/dashboard")
    else:
        if session['user_type'] == 'admin':
            cur = mysql.connection.cursor()
            cur.execute('SELECT count(*) FROM users WHERE user_type = "faculty"')
            faculty_count = cur.fetchall()
            cur.execute('SELECT count(*) FROM students')
            student_count = cur.fetchall()
            cur.execute('SELECT count(*) FROM books')
            books_count = cur.fetchall()
            cur.close()
    
            return render_template('/admin/adminhome.html', faculty = faculty_count, student = student_count, books = books_count)
        else:
            return render_template('/faculty/facultyhome.html')

@app.route("/profile", methods = ['GET','POST'])
def profile():
    if 'user' in session:
        if request.method == 'POST':
            name = request.form['name']
            mob = request.form['mob']
            email = request.form['email']

            cpass = request.form['cpass']
            npass = request.form['npass']
            cnfpass = request.form['cnfpass']
            files = request.files['img']

            if name and mob and email:
                cur = mysql.connection.cursor()
                cur.execute("UPDATE users SET name = %s, mob = %s, email = %s WHERE id = %s", (name, mob, email, session['id']))
                mysql.connection.commit()
                cur.close()
                flash(f'Profile information is successfully updated.')
            
            if cpass and npass and cnfpass:
                cur = mysql.connection.cursor()
                cur.execute("SELECT pass FROM users WHERE id = %s", (session['id'],))
                data = cur.fetchall()

                if bcrypt.check_password_hash(data[0][0], cpass):
                    pw_hash = bcrypt.generate_password_hash(npass).decode('utf-8')
                    cur.execute("UPDATE users SET pass = %s WHERE id = %s", (pw_hash, session['id']))
                    mysql.connection.commit()
                    cur.close()
                    flash('Password is successfully updated')
                else:
                    flash('Current password is incorrect.')
            
            if files:
                if files.filename == '':
                    pass
                
                if files and allowed_file(files.filename):
                    if secure_filename(files.filename):
                        im = Image.open(files)
                        ext = files.filename.split('.')[1]
                        filename = str(session['id'])+"."+ext
                        cur = mysql.connection.cursor()
                        cur.execute("UPDATE users SET profile_img = %s WHERE id = %s",(filename,session['id']))
                        mysql.connection.commit()
                        cur.close()
                        session['img'] = filename
                        im.save(os.path.join(app.config['UPLOAD_FOLDER'] + '\img', filename))
                        flash("Profile Picture Uploaded Successfully.")
                else:
                    flash('Please upload image in jpg, png and jpeg format only.')
            return redirect("/profile")
        
        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT name, mob, email FROM users WHERE mob = %s", (session['user'], ))
            data = cur.fetchall()
            cur.close()
            
            if session['user_type'] == 'admin':
                return render_template("/admin/profile.html", data = data)
            else:
                return render_template('/faculty/profile.html', data = data)
    
    else:
        return redirect("/")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/faculty")
def faculty():
    if 'user' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name, mob, email, user_type FROM users")
        data = cur.fetchall()
        cur.close()
        return render_template("/admin/faculty.html", data = data)
    else:
        return redirect('/')

@app.route("/addfaculty", methods = ['GET','POST'])
def addfaculty():
    if request.method == 'POST':
        name = request.form['name']
        mob = request.form['mob']
        email = request.form['email']
        upass = request.form['pass']
        usertype = request.form['type']

        cur = mysql.connection.cursor()
        cur.execute("SELECT mob FROM users where mob = %s",(mob,))
        data = cur.fetchall()
        if data:
            flash(f"{mob} is already exist in database.")
            return redirect("/addfaculty")
        else:
            # Below statement used to encrypt password with hash value
            ps_hash = bcrypt.generate_password_hash(upass).decode('utf-8')

            # Below statement used to verify password value
            # bcrypt.check_password_hash(pw_hash, 'hunter2') # returns True

            
            cur.execute("INSERT INTO users(name, mob, email, pass, user_type) VALUES (%s,%s,%s,%s,%s)", (name, mob, email, ps_hash, usertype))
            mysql.connection.commit()
            cur.close()
            flash(f'{name} is successfully added.')
            return redirect("/faculty")

    else:
        return render_template("admin/addfaculty.html")

@app.route("/logout")
def logout():
    session.pop('name', None)
    session.pop('user', None)
    session.pop('user_type', None)
    session.pop('img', None)
    return redirect("/")

@app.route("/books")
def book():
    if 'user' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, book_name, branch, year, pdf  FROM books")
        data = cur.fetchall()
        cur.close()
        
        if session['user_type'] == 'admin':
            return render_template("admin/booklist.html", data = data)
        else:
            return render_template('faculty/booklist.html', data = data)
    else:
        return redirect("/")

@app.route("/addbook", methods=['GET', 'POST'])
def addbook():
    if 'user' in session:
        if request.method == 'POST':
            bname = request.form['book_name']
            bdesc = request.form['book_des']
            branch = request.form['branch']
            year = request.form['year']
            file = request.files['book']
            pdf = pdfsave(file)
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO books(book_name, book_des, branch, year, pdf) VALUES (%s,%s,%s,%s,%s)", (bname, bdesc, branch, year, pdf))
            mysql.connection.commit()
            cur.close()
            return redirect ('/addbook')
        else:
            if session['user_type'] == 'admin':
                return render_template('admin/addbook.html')
            else:
                return render_template('faculty/addbook.html')
    else:
        return redirect('/')

def pdfsave(file):
    if file and pdf_allowed(file.filename):
        if secure_filename(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER']+'/files', file.filename))
            flash("Book Record Successfully Add.")
            return file.filename
            
def pdf_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in PDF_ALLOWED_EXTENSIONS

@app.route('/show/pdf/<filename>')
def openpdf(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER']+'/files', filename)


@app.route('/reset/<int:id>', methods = ['GET', 'POST'])
def resetAdmin(id):
    if 'user' in session:
        if session['user_type'] == 'admin':
            pw_hash = bcrypt.generate_password_hash('123').decode('utf-8')
            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET pass=%s WHERE id = %s",(pw_hash, id))
            mysql.connection.commit()
            cur.close()
            flash('Password is successfully reset.')
            return redirect('/faculty')
    else:
        return redirect('/')

@app.route('/remove/<int:id>', methods = ['GET'])
def removeUser(id):
    if 'user' in session:
        if session['user_type'] == 'admin':
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM users WHERE id = %s",(id,))
            mysql.connection.commit()
            cur.close()
            flash('User is successfully deleted.')
            return redirect('/faculty')
    else:
        return redirect('/')

@app.route('/removebook/<int:id>', methods = ['GET'])
def removeBook(id):
    if 'user' in session:
        if session['user_type'] == 'admin' or session['user_type'] == 'faculty':
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM books WHERE id = %s", (id,))
            mysql.connection.commit()
            cur.close()
            flash('Book is successfully deleted.')
            return redirect('/books')
    else:
        return redirect("/")

@app.route('/notification')
def notification():
    if 'user' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT id, title, des, branch, year, section, date FROM note')
        data = cur.fetchall()
        cur.close()
        
        if session['user_type'] == 'admin':
            return render_template('admin/notification.html', data = data)
        else:
            return render_template('faculty/notification.html', data = data)
    else:
        return redirect('/')

@app.route('/remove_notification/<int:id>')
def removeNotification(id):
    if 'user' in session:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM note WHERE id = %s', (id, ))
        mysql.connection.commit()
        cur.close()
        flash('Notification is successfully deleted.')
        return redirect('/notification')
        
    else:
        return redirect('/')

@app.route('/student', methods = ['GET', 'POST'])
def student():
    if 'user' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT id, student_name, mob, roll_no, branch, year, section FROM students')
        data = cur.fetchall()
        cur.close()
        if session['user_type'] == 'admin':
            return render_template('admin/students.html', data = data)
        else:
            return render_template('faculty/students.html', data = data)
    else:
        return redirect('/')

@app.route('/download')
def fileDownload():
    path = app.config['UPLOAD_FOLDER'] + "/files/Sample.xls"
    return send_file(path, as_attachment=True)

@app.route('/uploadstudent', methods = ['GET','POST'])
def uploadStudent():
    if 'user' in session:
        if request.method == 'POST':
            files = request.files['file']
            xl_file(files)
            
            book = xlrd.open_workbook(os.getcwd()+'/static/files/'+session['name']+'.xls')
            # xl_sheet_name = session['name']+'.xls'
            sheet = book.sheet_by_name('Sheet1')

            cur = mysql.connection.cursor()

            query = 'INSERT INTO students (student_name, mob, roll_no, branch, year, section, pass) VALUES (%s,%s,%s,%s,%s,%s,%s)'

            for r in range(1, sheet.nrows):
                name = sheet.cell(r,0).value
                mob = sheet.cell(r,1).value
                roll_no = sheet.cell(r,2).value
                branch = sheet.cell(r,3).value
                year = sheet.cell(r,4).value
                section = sheet.cell(r,5).value
                pw_hash = bcrypt.generate_password_hash('123')

                if name and mob and roll_no and branch and year and section and pw_hash:
                    value = (name, mob, roll_no, branch, year, section, pw_hash)
                    cur.execute(query, value)
                else:
                    break
            mysql.connection.commit()
            cur.close()
            return redirect("/student")

    else:
        return redirect('/')

@app.route('/removeStudent/<int:id>', methods = ['GET'])
def studetnRemove(id):
    if 'user' in session:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM students WHERE id = %s', (id, ))
        mysql.connection.commit()
        cur.close()
        flash('Student Record Delete Successfully.')
        return redirect('/student')
    else:
        return redirect('/')

def xl_file(file):
    if file and xl_allowed(file.filename):
        if secure_filename(file.filename):
            filename = session['name']+'.xls'
            file.save(os.path.join(app.config['UPLOAD_FOLDER']+'/files', filename))

def xl_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in XLS_ALLOWED_EXTENSIONS

# This is code for student portal pages

@app.route("/students", methods = ['GET', 'POST'])
def studentLogin():
    if 'user' in session:
        return redirect("/student_dashboard")

    elif request.method == 'POST':
        name = request.form['user']
        upass = request.form['pass']

        cur = mysql.connection.cursor()
        cur.execute('SELECT roll_no FROM students WHERE roll_no = %s', (name, ))
        data = cur.fetchall()

        if data:
            cur.execute('SELECT id, student_name, roll_no, branch, year, pass, profile_img FROM students WHERE roll_no = %s', (name, ))
            check = cur.fetchall()
            cur.close()

            pw_hash = check[0][5]
            if bcrypt.check_password_hash(pw_hash, upass):
                session['id'] = check[0][0]
                session['name'] = check[0][1]
                session['user'] = check[0][2]
                session['branch'] = check[0][3]
                session['year'] = check[0][4]
                session['img'] = check[0][6]

                return redirect('student_dashboard')
    else:        
        return render_template('student/login.html')

@app.route('/student_profile', methods = ['GET', 'POST'])
def studentProfile():
    if 'user' in session:
        
        if request.method == 'POST':
            name = request.form['name']
            mob = request.form['mob']

            cpass = request.form['cpass']
            npass = request.form['npass']
            cnfpass = request.form['cnfpass']
            files = request.files['img']

            if name and mob:
                cur = mysql.connection.cursor()
                cur.execute("UPDATE students SET student_name = %s, mob = %s WHERE id = %s", (name, mob, session['id']))
                mysql.connection.commit()
                cur.close()
                session['name'] = name
                # flash(f'Profile information is successfully updated.')
            
            if cpass and npass and cnfpass:
                cur = mysql.connection.cursor()
                cur.execute("SELECT pass FROM students WHERE id = %s", (session['id'],))
                data = cur.fetchall()

                if bcrypt.check_password_hash(data[0][0], cpass):
                    pw_hash = bcrypt.generate_password_hash(npass).decode('utf-8')
                    cur.execute("UPDATE students SET pass = %s WHERE id = %s", (pw_hash, session['id']))
                    mysql.connection.commit()
                    cur.close()
                    flash('Password is successfully updated')
                else:
                    flash('Current password is incorrect.')

            if files:
                if files.filename == '':
                    pass
                
                if files and allowed_file(files.filename):
                    if secure_filename(files.filename):
                        im = Image.open(files)
                        ext = files.filename.split('.')[1]
                        filename = str(session['id'])+"."+ext
                        cur = mysql.connection.cursor()
                        cur.execute("UPDATE students SET profile_img = %s WHERE id = %s",(filename,session['id']))
                        mysql.connection.commit()
                        cur.close()
                        session['img'] = filename
                        im.save(os.path.join(app.config['UPLOAD_FOLDER'] + '\img', filename))
                        flash("Profile Picture Uploaded Successfully.")
                else:
                    flash('Please upload image in jpg, png and jpeg format only.')
            return redirect("/student_profile")

        else:
            cur = mysql.connection.cursor()
            cur.execute('SELECT student_name, mob, roll_no, branch, year, section FROM students WHERE roll_no = %s', (session['user'], ))
            data = cur.fetchall()
            cur.close()
            return render_template('student/profile.html', data = data)

    else:
        return redirect('/students')

@app.route('/student_dashboard')
def studentDashboard():
    if 'user' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT id, title, des FROM note WHERE branch = %s AND year = %s',(session['branch'], session['year']))
        data = cur.fetchall()
        cur.close()
        return render_template('student/studenthome.html', data = data)
    else:
        return redirect('/students')

@app.route('/student_books')
def studentBooks():
    if 'user' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT book_name, pdf FROM books WHERE branch = %s and year = %s', (session['branch'], session['year']))
        data = cur.fetchall()
        cur.close()
        return render_template('student/booklist.html', data = data)
    else:
        return redirect('/students')

@app.route('/student_logout')
def studentLogout():
    session.pop('id', None)
    session.pop('name', None)
    session.pop('user', None)
    session.pop('img', None)
    session.pop('branch', None)
    session.pop('year', None)
    return redirect('/students')

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)