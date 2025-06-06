from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': role
    }

class Admin(User):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    special_permission = db.Column(db.String(100))  

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

class RegularUser(User):
    __tablename__ = 'regular_user'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    subscription_level = db.Column(db.String(50)) 

    __mapper_args__ = {
        'polymorphic_identity': 'regular_user',
    }

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    request_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50), default='new')
    date_opened = db.Column(db.DateTime, default=datetime.utcnow)
    date_closed = db.Column(db.DateTime)
    car_number = db.Column(db.String(20), nullable=False)
    master_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    master = db.relationship('User', foreign_keys=[master_id])
    
    customer_name = db.Column(db.String(200), nullable=False)  
    customer_phone = db.Column(db.String(20), nullable=False)  
    customer_email = db.Column(db.String(120), nullable=False) 

    user = db.relationship('User', foreign_keys=[user_id], backref='requests', lazy=True)

REQUEST_TYPES = {
    'repair': 'Ремонт',
    'maintenance': 'Техническое Обслуживание'
}

REQUEST_STATUSES = {
    'new': 'Новый',
    'in_work': 'В работе',
    'completed': 'Завершен'
}

