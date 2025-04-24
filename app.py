from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MySQL配置
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Dirdir123'
app.config['MYSQL_DB'] = 'flask_db'

def get_db():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('home.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT user_id, password FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
            
            if user and user['password'] == password:  # 注意：实际应用中应该使用密码哈希
                session['user_id'] = user['user_id']
                return redirect(url_for('index'))
            else:
                flash('用户名或密码错误')
        finally:
            db.close()
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                             (username, password, email))
                db.commit()
                flash('注册成功，请登录')
                return redirect(url_for('login'))
        except Exception as e:
            flash('注册失败，用户名或邮箱可能已存在')
        finally:
            db.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)