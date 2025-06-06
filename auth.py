from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Admin, RegularUser

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        phone = request.form['phone']
        full_name = request.form['full_name']
        role = request.form['role']
        
        if password != confirm_password:
            return "Пароли не совпадают, попробуйте снова."

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        if role == 'admin':
            new_user = Admin(username=username, password=hashed_password, email=email, phone=phone, full_name=full_name)
        else:
            new_user = RegularUser(username=username, password=hashed_password, email=email, phone=phone, full_name=full_name)

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        except:
            db.session.rollback()
            return 'Ошибка при регистрации'

    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('admin.dashboard'))  
        else:
            flash('Неверные учетные данные. Пожалуйста, попробуйте снова.', 'error')
            return redirect(url_for('auth.login'))  
    return render_template('login.html')
@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('auth.login'))

