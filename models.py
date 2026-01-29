from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(20), nullable=False) # Admin, RoastManager, Cupper
    is_active = db.Column(db.Boolean, default=True)

class CoffeeSample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_id = db.Column(db.String(20), unique=True, nullable=False) # Auto-generated SHB-XXXX
    coffee_type = db.Column(db.String(50)) # Variety/Genetic
    origin = db.Column(db.String(100)) # Country
    region = db.Column(db.String(100))
    farm = db.Column(db.String(100))
    process = db.Column(db.String(50))
    harvest_year = db.Column(db.String(10))
    ico_number = db.Column(db.String(50)) # ICO ID
    certifications = db.Column(db.String(200)) # Fair Trade, Organic, etc.
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class PhysicalAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample_id = db.Column(db.Integer, db.ForeignKey('coffee_sample.id'), nullable=False)
    moisture = db.Column(db.Float)
    density = db.Column(db.Float)
    roast_level = db.Column(db.String(20))
    bean_color = db.Column(db.String(50)) # Green-blue, Pale, etc.
    defects_cat1 = db.Column(db.Integer)
    defects_cat2 = db.Column(db.Integer)
    screen_size = db.Column(db.String(50))
    notes = db.Column(db.Text)
    assessed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class CuppingSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roast_level = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Planned') # Planned, Open, Closed
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class SessionSample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('cupping_session.id'), nullable=False)
    sample_id = db.Column(db.Integer, db.ForeignKey('coffee_sample.id'), nullable=False)
    blind_code = db.Column(db.String(50)) # e.g. "Sample A"
    assigned_cupper_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # Relationships for easier template access
    cupping_session = db.relationship('CuppingSession', backref='session_samples')
    coffee_sample = db.relationship('CoffeeSample', backref='session_links')
    assigned_cupper = db.relationship('User', foreign_keys=[assigned_cupper_id], backref='assigned_samples')

class SensoryEvaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_sample_id = db.Column(db.Integer, db.ForeignKey('session_sample.id'), nullable=False)
    cupper_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    session_sample = db.relationship('SessionSample', backref='evaluations')
    cupper = db.relationship('User', backref='evaluations')

    aroma = db.Column(db.Float) # 0-10
    flavor = db.Column(db.Float)
    aftertaste = db.Column(db.Float)
    acidity = db.Column(db.Float)
    body = db.Column(db.Float)
    sweetness = db.Column(db.Float)
    balance = db.Column(db.Float)
    clean_cup = db.Column(db.Float)
    overall = db.Column(db.Float)
    uniformity = db.Column(db.Integer, default=10)
    defects = db.Column(db.Float, default=0) # Negative pts
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
