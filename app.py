from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pymysql
import os
from datetime import datetime

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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM logs WHERE user_id = %s ORDER BY create_time DESC", (session['user_id'],))
            logs = cursor.fetchall()
        return render_template('home.html', logs=logs)
    finally:
        db.close()

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

@app.route('/log', methods=['POST'])
def create_log():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})
    
    title = request.form.get('title')
    content = request.form.get('content')
    
    if not title or not content:
        return jsonify({'success': False, 'message': '标题和内容不能为空'})
    
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO logs (user_id, title, content) VALUES (%s, %s, %s)",
                         (session['user_id'], title, content))
            db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': '创建日志失败'})
    finally:
        db.close()

@app.route('/log', methods=['PUT'])
def update_log():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})
    
    log_id = request.form.get('log_id')
    title = request.form.get('title')
    content = request.form.get('content')
    
    if not log_id or not title or not content:
        return jsonify({'success': False, 'message': '参数不完整'})
    
    db = get_db()
    try:
        with db.cursor() as cursor:
            # 检查日志是否属于当前用户
            cursor.execute("SELECT user_id FROM logs WHERE log_id = %s", (log_id,))
            log = cursor.fetchone()
            if not log or log['user_id'] != session['user_id']:
                return jsonify({'success': False, 'message': '无权修改此日志'})
            
            cursor.execute("UPDATE logs SET title = %s, content = %s WHERE log_id = %s",
                         (title, content, log_id))
            db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': '更新日志失败'})
    finally:
        db.close()

@app.route('/log', methods=['DELETE'])
def delete_log():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '请先登录'})
    
    data = request.get_json()
    log_id = data.get('log_id')
    
    if not log_id:
        return jsonify({'success': False, 'message': '参数不完整'})
    
    db = get_db()
    try:
        with db.cursor() as cursor:
            # 检查日志是否属于当前用户
            cursor.execute("SELECT user_id FROM logs WHERE log_id = %s", (log_id,))
            log = cursor.fetchone()
            if not log or log['user_id'] != session['user_id']:
                return jsonify({'success': False, 'message': '无权删除此日志'})
            
            cursor.execute("DELETE FROM logs WHERE log_id = %s", (log_id,))
            db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': '删除日志失败'})
    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)