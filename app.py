from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 请更改为随机密钥

# 数据库配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Dirdir123',
    'database': 'flask_db'
}

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误')
        
        cursor.close()
        conn.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        try:
            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)',
                         (username, hashed_password, email))
            conn.commit()
            flash('注册成功，请登录')
            return redirect(url_for('login'))
        except:
            flash('用户名或邮箱已存在')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('register.html')

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

# 获取所有日志
@app.route('/api/logs')
@login_required
def get_logs():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM logs WHERE user_id = %s ORDER BY created_at DESC', (session['user_id'],))
    logs = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return jsonify(logs)

# 获取单个日志
@app.route('/api/logs/<int:log_id>')
@login_required
def get_log(log_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM logs WHERE log_id = %s AND user_id = %s', (log_id, session['user_id']))
    log = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if log:
        return jsonify(log)
    return jsonify({'error': '日志不存在'}), 404

# 创建日志
@app.route('/api/logs', methods=['POST'])
@login_required
def create_log():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    
    if not title or not content:
        return jsonify({'error': '标题和内容不能为空'}), 400
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO logs (user_id, title, content) VALUES (%s, %s, %s)',
                      (session['user_id'], title, content))
        conn.commit()
        return jsonify({'message': '日志创建成功'})
    except:
        return jsonify({'error': '创建日志失败'}), 500
    finally:
        cursor.close()
        conn.close()

# 更新日志
@app.route('/api/logs/<int:log_id>', methods=['PUT'])
@login_required
def update_log(log_id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    
    if not title or not content:
        return jsonify({'error': '标题和内容不能为空'}), 400
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE logs SET title = %s, content = %s WHERE log_id = %s AND user_id = %s',
                      (title, content, log_id, session['user_id']))
        if cursor.rowcount == 0:
            return jsonify({'error': '日志不存在或无权修改'}), 404
        conn.commit()
        return jsonify({'message': '日志更新成功'})
    except:
        return jsonify({'error': '更新日志失败'}), 500
    finally:
        cursor.close()
        conn.close()

# 删除日志
@app.route('/api/logs/<int:log_id>', methods=['DELETE'])
@login_required
def delete_log(log_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM logs WHERE log_id = %s AND user_id = %s',
                      (log_id, session['user_id']))
        if cursor.rowcount == 0:
            return jsonify({'error': '日志不存在或无权删除'}), 404
        conn.commit()
        return jsonify({'message': '日志删除成功'})
    except:
        return jsonify({'error': '删除日志失败'}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True) 