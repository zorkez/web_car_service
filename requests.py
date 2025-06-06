from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Request, User
from datetime import datetime

requests = Blueprint('requests', __name__)

@requests.route('/request_repair', methods=['GET', 'POST'])
def request_repair():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))  

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user_id = session['user_id']
        request_type = request.form['request_type']
        description = request.form['description']
        car_number = request.form['car_number']
        status = 'new'
        
        if user.role == 'admin':
            status = request.form['status']
            customer_name = request.form['customer_name']
            customer_phone = request.form['customer_phone']
            customer_email = request.form['customer_email']
        else:
            customer_name = user.full_name  
            customer_phone = user.phone     
            customer_email = user.email     
        
        master_name = request.form['master']
        master = User.query.filter_by(full_name=master_name, role='admin').first()

        new_request = Request(
            user_id=user_id,
            request_type=request_type,
            description=description,
            car_number=car_number,
            status=status,
            master=master,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email
        )

        try:
            db.session.add(new_request)
            db.session.commit()
            return redirect(url_for('admin.dashboard'))  
        except Exception as e:
            db.session.rollback()
            return f'Ошибка при создании заявки: {e}'

    masters = User.query.filter_by(role='admin').all()
    return render_template('request_repair.html', masters=masters)

@requests.route('/edit_request/<int:request_id>', methods=['GET', 'POST'])
def edit_request(request_id):
    req = Request.query.get_or_404(request_id)

    if req.user_id != session.get('user_id') and session['role'] != 'admin':
        return "Ошибка: Вы не можете редактировать чужую заявку."

    if req.status in ['in_work', 'completed'] and session['role'] == 'regular_user':
        return "Ошибка: Вы не можете редактировать заявку, так как она уже в работе или завершена."

    if request.method == 'POST':
        req.request_type = request.form['request_type']
        req.description = request.form['description']
        req.car_number = request.form['car_number']

        if session['role'] == 'regular_user':
            req.status = 'new'
            req.date_opened = req.date_opened  
            req.date_closed = req.date_closed  
        else:
            req.status = request.form['status']
            if 'date_opened' in request.form and request.form['date_opened']:
                req.date_opened = datetime.strptime(request.form['date_opened'], '%Y-%m-%dT%H:%M')
            if 'date_closed' in request.form and request.form['date_closed']:
                req.date_closed = datetime.strptime(request.form['date_closed'], '%Y-%m-%dT%H:%M')

        master_name = request.form['master']
        master = User.query.filter_by(full_name=master_name, role='admin').first()
        req.master = master

        try:
            db.session.commit()
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            return f"Ошибка при обновлении заявки: {e}"

    masters = User.query.filter_by(role='admin').all()
    return render_template('edit_request.html', request=req, masters=masters)

@requests.route('/delete_request/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    req = Request.query.get_or_404(request_id)
    
    if req.user_id != session.get('user_id') and session['role'] != 'admin':
        return "Ошибка: Вы не можете удалить чужую заявку."

    try:
        db.session.delete(req)
        db.session.commit()
        return redirect(url_for('admin.dashboard'))
    except Exception as e:
        db.session.rollback()
        return f"Ошибка при удалении заявки: {e}"
