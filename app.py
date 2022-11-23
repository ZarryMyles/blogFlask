from flask import *
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'tester'
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_DB'] = 'blog'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = 'SDFLKJSFDKJSDLAJKLKJSADFKN'
mysql = MySQL(app)

status = {'logged_in': False, 'email': ''}


def register_check(name, email, password, password_confirm):
    if (password != password_confirm or len(password) < 8 or len(name) == 0 or len(email) == 0):
        return False
# check if email is already present
    return True


@app.route('/')
def index():
    if status['logged_in']:
        print(f'logged in with email {status["email"]}')
        # return render_template("dashboard.html")
        return redirect(url_for('dashboard'))
    else:
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM posts")
        print(result)
        posts = cur.fetchall()
        if result > 0:
            return render_template('home.html', posts=posts)
        else:
            msg = 'No Articles Found'
            return render_template('home.html', msg=msg)


#   register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        password_confirm = request.form['passwordConfirmation']
        if (register_check(name, email, password, password_confirm)):
            cur = mysql.connection.cursor()
            # print('''INSERT INTO authors values('%s','%s','%s')''' % (email,name,password))
            # cur.execute('''INSERT INTO authors values('%s','%s','%s')''' , (email,name,password))
            try:
                cur.execute(
                    'INSERT INTO authors(name,email,passwd) VALUES (%s, %s ,%s)', (name, email, password))
                mysql.connection.commit()
                flash(f'{email} has been added')
                return render_template('login.html')
            except:
                return render_template('register.html', error='User Exists')
            # return f'username = {name} and email = {email} password = {password} password2 = {password_confirm}'
        else:
            return render_template('register.html', error='Invalid Input')
    else:
        return render_template('register.html', error='')

# login input check


def login_check(email, password):
    if (len(email) == 0 or len(password) < 8):
        return False
    return True

# passwordcheck


def passwordverify(password_data, password):
    if password == password_data:
        return True
    return False

# login


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']
        if (login_check(email, password)):
            cur = mysql.connection.cursor()
            result = cur.execute(
                "SELECT * FROM authors WHERE email = %s", [email])
            if result > 0:
                data = cur.fetchone()
                password_data = data['passwd']
                if passwordverify(password, password_data):
                    status['logged_in'] = True
                    status['email'] = email

                    flash('You are now logged in', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    error = 'Invalid login'
                    return render_template('login.html', error=error)
                # cur.close()
                # return (f'{email},{password}')
            else:
                error = 'Invalid Credentials'
                return render_template('login.html', error=error)
        else:
            error = 'Please enter correct details'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')

# signout


@app.route('/signout', methods=['GET', 'POST'])
def signout():
    status['logged_in'] = False
    status['email'] = ''
    return redirect(url_for('index'))

# dashboard


@app.route('/dashboard')
def dashboard():
    if (status['logged_in']):
        cur = mysql.connection.cursor()
        result = cur.execute(
            "SELECT * FROM posts ")
        print(result)
        posts = cur.fetchall()
        if result > 0:
            return render_template('dashboard.html', name=status['email'], posts=posts)
        else:
            msg = 'No Articles Found'
            return render_template('dashboard.html', msg=msg)
    else:
        return redirect(url_for('index'))


# myposts
@app.route('/myposts')
def myposts():
    cur = mysql.connection.cursor()
    result = cur.execute(
        "SELECT * FROM posts WHERE email = %s", [status["email"]])
    posts = cur.fetchall()
    if result > 0:
        return render_template('myposts.html', name=status['email'], posts=posts)
    else:
        msg = 'No Articles Found'
        return render_template('myposts.html', msg=msg)

# create post


@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST' and status['logged_in']:
        title = request.form['title'].strip()
        post = request.form['post'].strip()
        email = status['email']
        if (len(title) != 0 and len(post) != 0):
            try:
                cur = mysql.connection.cursor()
                cur.execute(
                    'INSERT INTO posts(email,title,post) VALUES (%s, %s ,%s)', (email, title, post))
                mysql.connection.commit()
                flash(f'{email} has been added')
                return redirect(url_for('dashboard'))
            except:
                return render_template('create_post.html', error='Entry exists')
        return render_template('create_post.html', error='Invalid Entry')
    else:
        return render_template('create_post.html')


# ---------deleteposts
@app.route('/deletepost', methods=['GET', 'POST'])
def deletepost():
    if request.method == 'POST' and status['logged_in']:
        title = request.form['title'].strip()
        email = status['email']
        if (len(title) != 0):
            try:
                cur = mysql.connection.cursor()
                cur.execute(
                    'DELETE FROM posts WHERE email = %s and title = %s', (email, title))
                mysql.connection.commit()
                return redirect(url_for('myposts'))
            except:
                return redirect(url_for('myposts', error='exception'))
        else:
            return redirect(url_for('myposts', error='Empty'))
    else:
        return redirect(url_for('myposts', error='not logged in'))


# updatepost
@app.route('/update_post', methods=['GET', 'POST'])
def update_post():
    if request.method == 'POST':
        if (status['logged_in']):
            oldtitle = request.form['oldtitle'].strip()
            title = request.form['title'].strip()
            post = request.form['post'].strip()
            email = status['email']
            try:
                cur = mysql.connection.cursor()
                cur.execute(
                    'UPDATE posts SET title = %s , post = %s WHERE title = %s and email = %s', (title, post, oldtitle, email))
                mysql.connection.commit()
                return redirect(url_for('myposts'))

            except:
                render_template("update_post.html")

            email = status['email']

        else:
            redirect(url_for('index'))
    else:
        cur = mysql.connection.cursor()
        result = cur.execute(
            "SELECT * FROM posts WHERE email = %s", [status["email"]])
        posts = cur.fetchall()
        if result > 0:
            return render_template("update_post.html", posts=posts)
        else:
            msg = 'No Articles Found'
            return render_template("update_post.html", msg=msg)
        # return render_template("update_post.html")


# ----------posts

@app.route('/posts')
def articles():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM posts")
    posts = cur.fetchall()
    if result > 0:
        return render_template('posts.html', posts=posts)
    else:
        msg = 'No Articles Found'
        return render_template('posts.html', msg=msg)


# ----------post
@app.route('/post/<string:title>/')
def article(title):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM posts WHERE id = %s", [title])
    posts = cur.fetchone()
    return render_template('posts.html', posts=posts)


app.run(debug=True)
