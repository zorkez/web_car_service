from flask import Blueprint, render_template, session, redirect, url_for, request
from models import db, Request, User
from math import ceil
from datetime import datetime
import pandas as pd

admin = Blueprint('admin', __name__)

@admin.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login')) 

    user = User.query.get(session['user_id'])
    current_year = datetime.now().year  
    
    page = request.args.get('page', 1, type=int)
    per_page = 10

    if user.role == 'admin':
        total_requests = Request.query.count()  
        requests = Request.query.offset((page - 1) * per_page).limit(per_page).all()
    else:
        total_requests = Request.query.filter_by(user_id=user.id).count()  
        requests = Request.query.filter_by(user_id=user.id).offset((page - 1) * per_page).limit(per_page).all()

    total_pages = ceil(total_requests / per_page)  
    
    return render_template('dashboard.html', requests=requests, current_year=current_year, page=page, total_pages=total_pages)
    
@admin.route('/calculate_forecast', methods=['POST'])
def calculate_forecast():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))  

    selected_month = int(request.form['month'])
    selected_year = int(request.form['year']) 
    
    requests_data = Request.query.all()
    
    data = []
    for req in requests_data:
        data.append({
            'month': req.date_opened.month,
            'year': req.date_opened.year,
            'requests': 1 
        })

    df = pd.DataFrame(data)
    
    df_month = df.groupby(['year', 'month']).sum().reset_index()

    prev_months = [(selected_year, selected_month - 3), (selected_year, selected_month - 2), (selected_year, selected_month - 1)]

    missing_months = []
    for month in prev_months:
        if not ((df_month['year'] == month[0]) & (df_month['month'] == month[1])).any():
            missing_months.append(month)

    if missing_months:
        for month in missing_months:
            new_data = pd.DataFrame([{'year': month[0], 'month': month[1], 'requests': 0}])
            df_month = pd.concat([df_month, new_data], ignore_index=True)

    if selected_month in [1, 2, 3]: 
        prev_months = [(selected_year - 1, 12), (selected_year, selected_month - 2), (selected_year, selected_month - 1)]
    else:
        prev_months = [(selected_year, selected_month - 3), (selected_year, selected_month - 2), (selected_year, selected_month - 1)]

    df_filtered = df_month[
        ((df_month['year'] == prev_months[0][0]) & (df_month['month'] == prev_months[0][1])) |
        ((df_month['year'] == prev_months[1][0]) & (df_month['month'] == prev_months[1][1])) |
        ((df_month['year'] == prev_months[2][0]) & (df_month['month'] == prev_months[2][1]))
    ]
    
    df_filtered['rolling_avg'] = df_filtered['requests'].rolling(window=3).mean() 
    
    if df_filtered.empty or df_filtered['rolling_avg'].isna().all():
        return f"Недостаточно данных для расчета прогноза на {selected_month}/{selected_year}."

    forecast = df_filtered['rolling_avg'].iloc[-1] 

    return f"Прогнозное количество заявок для {selected_month}/{selected_year} месяца: {forecast:.2f}"
