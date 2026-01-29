from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, CoffeeSample, PhysicalAssessment, CuppingSession, SessionSample, SensoryEvaluation
import bcrypt
import datetime
import os
import re
import shutil

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Critical for Sessions on Render
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'shibam-secret-key-123-hardcoded')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shibam_db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)
# Relaxing security for debugging login loop
app.config['SESSION_COOKIE_SECURE'] = False 
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

ADMIN_SECRET_KEY = "SHIBAM-KEY"

def backup_db():
    try:
        basedir = os.path.abspath(os.path.dirname(__file__))
        source = os.path.join(basedir, 'shibam_db.sqlite')
        backups_dir = os.path.join(basedir, 'backups')
        
        if os.path.exists(source):
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
            dest = os.path.join(backups_dir, f'backup-{timestamp}.sqlite')
            os.makedirs(backups_dir, exist_ok=True)
            shutil.copy2(source, dest)
            # Keep only last 5 backups
            if os.path.exists(backups_dir):
                backups = sorted([os.path.join(backups_dir, f) for f in os.listdir(backups_dir)])
                if len(backups) > 5:
                    for old_b in backups[:-5]:
                        try:
                            os.remove(old_b)
                        except:
                            pass
    except Exception as e:
        print(f"Backup failed: {e}")

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    return True, ""

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None

# --- Utils ---
def get_translations(lang):
    if lang == 'en':
        return {
            'dir': 'ltr', 'align': 'left',
            'app_title': 'Shibam Al-Maaref System',
            'login': 'Login', 'logout': 'Logout', 'dashboard': 'Dashboard',
            'samples': 'Samples', 'sessions': 'Sessions', 'reports': 'Reports',
            'username': 'Username', 'password': 'Password', 'role': 'Role',
            'welcome': 'Welcome', 'add_sample': 'Register Sample',
            'origin': 'Origin', 'farm': 'Farm', 'process': 'Processing',
            'harvest': 'Harvest Year', 'save': 'Save', 'physical': 'Physical Grading',
            'sensory': 'Sensory Cupping', 'aroma': 'Aroma', 'flavor': 'Flavor',
            'acidity': 'Acidity', 'body': 'Body', 'sweetness': 'Sweetness',
            'balance': 'Balance', 'clean_cup': 'Clean Cup', 'overall': 'Overall',
            'submit': 'Submit', 'register': 'Register', 'confirm_password': 'Confirm Password',
            'full_name': 'Full Name', 'email': 'Email', 'admin_key': 'Admin Secret Key',
            'lang_toggle': 'العربية', 'enter_lab': 'Enter Lab', 'staff_login': 'Staff Login',
            'cupper_role': 'Sensory Cupper', 'staff_role': 'Scientific Staff',
            'cupper_desc': '',
            'staff_desc': '',
            'back': 'Back', 'auth_login': 'Auth Login',
            'manage_users': 'Manage Users', 'add_user': 'Add User'
        }
    else:
        return {
            'dir': 'rtl', 'align': 'right',
            'app_title': 'نظام شبام المعارف',
            'login': 'تسجيل الدخول', 'logout': 'تسجيل الخروج', 'dashboard': 'لوحة التحكم',
            'samples': 'المخزون والعينات', 'sessions': 'جلسات التذوق', 'reports': 'التقارير والنتائج',
            'username': 'اسم المستخدم', 'password': 'كلمة المرور', 'role': 'الدور الوظيفي',
            'welcome': 'مرحباً بكم', 'add_sample': 'تسجيل عينة جديدة',
            'origin': 'بلد المنشأ', 'farm': 'المزرعة / المصدر', 'process': 'طريقة المعالجة',
            'harvest': 'موسم الحصاد', 'save': 'حفظ البيانات', 'physical': 'التقييم الفيزيائي',
            'sensory': 'التقييم الحسي (Cupping)', 'aroma': 'الرائحة', 'flavor': 'النكهة',
            'acidity': 'الحموضة', 'body': 'القوام', 'sweetness': 'الحلاوة',
            'balance': 'التوازن', 'clean_cup': 'نظافة الكوب', 'overall': 'التقييم العام',
            'submit': 'إرسال التقييم', 'register': 'إنشاء حساب جديد', 'confirm_password': 'تأكيد كلمة المرور',
            'full_name': 'الاسم الكامل', 'email': 'البريد الإلكتروني', 'admin_key': 'الرمز السري للإدارة',
            'lang_toggle': 'English', 'enter_lab': 'دخول المختبر', 'staff_login': 'دخول الموظفين',
            'cupper_role': 'متذوق حسي معتمد', 'staff_role': 'الطاقم العلمي والإداري',
            'cupper_desc': '',
            'staff_desc': '',
            'back': 'رجوع', 'auth_login': 'تحقق ودخول',
            'manage_users': 'إدارة المستخدمين', 'add_user': 'إضافة حساب جديد'
        }

@app.before_request
def set_lang():
    if 'lang' not in session:
        session['lang'] = 'ar'

@app.route('/toggle_lang')
def toggle_lang():
    session['lang'] = 'en' if session.get('lang') == 'ar' else 'ar'
    return redirect(request.referrer or url_for('index'))



# --- Routes ---
@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('welcome'))
    
    # ROLE-BASED DIRECT ROUTING (Real-world workflow)
    if current_user.role == 'RoastManager':
        return redirect(url_for('physical_grading'))
    
    if current_user.role == 'Cupper':
        # Dashboard for cuppers shows active sessions for evaluation
        assigned_samples = SessionSample.query.join(CuppingSession).filter(CuppingSession.status == 'Open').all()
        return render_template('dashboard.html', 
                             t=get_translations(session['lang']), 
                             assigned_samples=assigned_samples)

    # Admin View
    assigned_samples = SessionSample.query.join(CuppingSession).filter(CuppingSession.status == 'Open').all()
    return render_template('dashboard.html', 
                         t=get_translations(session['lang']), 
                         assigned_samples=assigned_samples)

@app.route('/welcome')
def welcome():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('welcome.html', t=get_translations(session['lang']))

@app.route('/cupper-selection', methods=['GET', 'POST'])
def cupper_selection():
    if not session.get('lab_verified'):
        return redirect(url_for('welcome'))
    
    if request.method == 'POST':
        cupper_id = request.form.get('cupper_id')
        user = User.query.get(cupper_id)
        if user and user.role == 'Cupper':
            login_user(user)
            session.pop('lab_verified', None)
            return redirect(url_for('index'))
            
    cuppers = User.query.filter_by(role='Cupper', is_active=True).all()
    return render_template('cupper_selection.html', cuppers=cuppers, t=get_translations(session['lang']))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        if role == 'Cupper':
            lab_code = request.form.get('lab_code')
            if lab_code != "SHIBAM-LAB":
                flash('Invalid Lab Access Code! Please use the company authorized code.')
                return redirect(url_for('welcome'))
            
            # Pass the lab code verification to the next step
            session['lab_verified'] = True
            return redirect(url_for('cupper_selection'))
        elif role == 'Admin':
            username = request.form.get('username')
            password = request.form.get('password')
            secret_key = request.form.get('secret_key')
            
            print(f"DEBUG LOGIN: User={username}, KeyEntered='{secret_key}', KeyExpected='{ADMIN_SECRET_KEY}'")
            
            if secret_key != ADMIN_SECRET_KEY:
                flash(f'Invalid Admin Secret Key! You entered: {secret_key}')
                return render_template('login.html', t=get_translations(session['lang']))
                
            user = User.query.filter_by(username=username, role='Admin').first()
            if user:
                # Direct check for admin123 as fallback, or bcrypt check
                is_valid = (password == "admin123") or bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))
                if is_valid:
                    if not user.is_active:
                        flash('Your account is deactivated. Please contact Admin.')
                        return render_template('login.html', t=get_translations(session['lang']))
                    login_user(user, remember=True)
                    # Redirect directly to specific dashboard to avoid loops
                    return redirect(url_for('admin_sessions'))
            flash('Invalid credentials for Admin.')
        else: # Handles RoastManager and other potential roles
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = User.query.filter_by(username=username, role=role).first()
            if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                if not user.is_active:
                    flash('Your account is deactivated. Please contact Admin.')
                    return render_template('login.html', t=get_translations(session['lang']))
                login_user(user)
                # Success - dynamic redirect
                if user.role == 'RoastManager':
                    print(f"DEBUG: Redirecting Roaster {user.username} to physical grading")
                    return redirect(url_for('physical_grading'))
                return redirect(url_for('index'))
            flash('Invalid credentials')
            
    return render_template('login.html', t=get_translations(session['lang']))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    # Only Admin can create new accounts now
    if current_user.role != 'Admin':
        return "Access Denied", 403
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        secret_key = request.form.get('secret_key')

        # Password Strength Check
        is_valid, msg = validate_password(password)
        if not is_valid:
            flash(msg)
            return render_template('register.html', t=get_translations(session['lang']))

        if password != confirm_password:
            flash('Passwords do not match!')
            return render_template('register.html', t=get_translations(session['lang']))

        if role == 'Admin' and secret_key != ADMIN_SECRET_KEY:
            flash('Invalid Admin Secret Key for registration!')
            return render_template('register.html', t=get_translations(session['lang']))


        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or Email already exists!')
            return render_template('register.html', t=get_translations(session['lang']))

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            password_hash=hashed_password,
            role=role if role else 'Cupper',
            is_active=True
        )
        db.session.add(new_user)
        db.session.commit()
        backup_db() 
        flash(f'User {new_user.username} created successfully!')
        print(f"DEBUG: Admin created {new_user.username} as {new_user.role}")
        return redirect(url_for('admin_users'))
    
    return render_template('register.html', t=get_translations(session['lang']))

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'Admin': return "Access Denied", 403
    users = User.query.all()
    return render_template('admin_users.html', users=users, t=get_translations(session['lang']))

@app.route('/admin/user/delete/<int:id>')
@login_required
def delete_user(id):
    if current_user.role != 'Admin': return "Denied", 403
    if id == current_user.id:
        flash("Cannot delete yourself!")
        return redirect(url_for('admin_users'))
    
    user = User.query.get_or_404(id)
    try:
        # Delete related data first to avoid foreign key issues
        SensoryEvaluation.query.filter_by(cupper_id=id).delete()
        PhysicalAssessment.query.filter_by(assessed_by=id).delete()
        
        db.session.delete(user)
        db.session.commit()
        flash("User and all their associated evaluations deleted successfully.")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {str(e)}")
        print(f"Delete Error: {e}")
        
    return redirect(url_for('admin_users'))

@app.route('/admin/sample/delete/<int:id>')
@login_required
def delete_sample(id):
    if current_user.role != 'Admin': return "Denied", 403
    sample = CoffeeSample.query.get_or_404(id)
    # Also delete related assessments and session links
    PhysicalAssessment.query.filter_by(sample_id=id).delete()
    SessionSample.query.filter_by(sample_id=id).delete()
    db.session.delete(sample)
    db.session.commit()
    flash("Sample and related data deleted.")
    return redirect(url_for('admin_samples'))

@app.route('/admin/sample/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_sample(id):
    if current_user.role != 'Admin': return "Denied", 403
    sample = CoffeeSample.query.get_or_404(id)
    if request.method == 'POST':
        sample.coffee_type = request.form.get('coffee_type')
        sample.origin = request.form.get('origin')
        sample.region = request.form.get('region')
        sample.farm = request.form.get('farm')
        sample.process = request.form.get('process')
        sample.harvest_year = request.form.get('harvest_year')
        sample.ico_number = request.form.get('ico_number')
        sample.certifications = request.form.get('certifications')
        db.session.commit()
        flash("Sample updated successfully.")
        return redirect(url_for('admin_samples'))
    return render_template('edit_sample.html', s=sample, t=get_translations(session['lang']))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Admin Routes ---
@app.route('/admin/samples', methods=['GET', 'POST'])
@login_required
def admin_samples():
    if current_user.role != 'Admin': return "Access Denied", 403
    if request.method == 'POST':
        sid = f"SHB-{datetime.datetime.now().strftime('%Y%j%H%M')}"
        new_sample = CoffeeSample(
            sample_id=sid,
            coffee_type=request.form.get('coffee_type'),
            origin=request.form.get('origin'),
            region=request.form.get('region'),
            farm=request.form.get('farm'),
            process=request.form.get('process'),
            harvest_year=request.form.get('harvest_year'),
            ico_number=request.form.get('ico_number'),
            certifications=request.form.get('certifications')
        )
        db.session.add(new_sample)
        db.session.commit()
    samples = CoffeeSample.query.all()
    return render_template('admin_samples.html', samples=samples, t=get_translations(session['lang']))

@app.route('/admin/sessions', methods=['GET', 'POST'])
@login_required
def admin_sessions():
    if current_user.role != 'Admin': return "Access Denied", 403
    if request.method == 'POST':
        if 'create_session' in request.form:
            sess = CuppingSession(name=request.form.get('name'), roast_level=request.form.get('roast_level'), status='Open')
            db.session.add(sess)
            db.session.commit()
        elif 'link_sample' in request.form:
            cupper_id = request.form.get('assigned_cupper_id')
            ls = SessionSample(
                session_id=request.form.get('session_id'),
                sample_id=request.form.get('sample_id'),
                blind_code=request.form.get('blind_code'),
                assigned_cupper_id=int(cupper_id) if cupper_id else None
            )
            db.session.add(ls)
            db.session.commit()
            
    sessions = CuppingSession.query.all()
    samples = CoffeeSample.query.all()
    users = User.query.all()
    all_evaluations = SensoryEvaluation.query.all()
    return render_template('admin_sessions.html', 
                         sessions=sessions, 
                         samples=samples, 
                         users=users,
                         all_evaluations=all_evaluations,
                         t=get_translations(session['lang']))

@app.route('/admin/session/toggle/<int:id>')
@login_required
def toggle_session(id):
    if current_user.role != 'Admin': return "Denied", 403
    sess = CuppingSession.query.get_or_404(id)
    sess.status = 'Closed' if sess.status == 'Open' else 'Open'
    db.session.commit()
    return redirect(url_for('admin_sessions'))

@app.route('/admin/user/toggle/<int:id>')
@login_required
def toggle_user(id):
    if current_user.role != 'Admin': return "Denied", 403
    user = User.query.get_or_404(id)
    user.is_active = not user.is_active
    db.session.commit()
    return redirect(url_for('admin_sessions'))

# --- Manager Routes ---
@app.route('/manager/physical', methods=['GET', 'POST'])
@login_required
def physical_grading():
    if current_user.role not in ['Admin', 'RoastManager']: return "Access Denied", 403
    if request.method == 'POST':
        grad = PhysicalAssessment(
            sample_id=request.form.get('sample_id'),
            moisture=request.form.get('moisture'),
            density=request.form.get('density'),
            roast_level=request.form.get('roast_level'),
            bean_color=request.form.get('bean_color'),
            defects_cat1=request.form.get('cat1'),
            defects_cat2=request.form.get('cat2'),
            screen_size=request.form.get('screen'),
            notes=request.form.get('notes'),
            assessed_by=current_user.id
        )
        db.session.add(grad)
        db.session.commit()
    samples = CoffeeSample.query.all()
    return render_template('manager_physical.html', samples=samples, t=get_translations(session['lang']))

@app.route('/admin/export/<int:session_id>')
@login_required
def export_excel(session_id):
    if current_user.role != 'Admin': return "Denied", 403
    
    import pandas as pd
    import io
    
    sess = CuppingSession.query.get_or_404(session_id)
    evals = SensoryEvaluation.query.join(SessionSample).filter(SessionSample.session_id == session_id).all()
    
    data = []
    for e in evals:
        data.append({
            'Session': sess.name,
            'Blind Code': e.session_sample.blind_code,
            'Cupper': e.cupper.full_name,
            'Aroma': e.aroma,
            'Flavor': e.flavor,
            'Acidity': e.acidity,
            'Body': e.body,
            'Sweetness': e.sweetness,
            'Balance': e.balance,
            'Total Score': e.aroma + e.flavor + e.acidity + e.body + e.sweetness + e.balance + e.clean_cup + e.overall - e.defects,
            'Notes': e.notes
        })
    
    if not data:
        flash("No evaluation data found for this session to export.")
        return redirect(url_for('admin_sessions'))
        
    df = pd.DataFrame(data)
    
    try:
        import xlsxwriter
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Evaluations')
        writer.close()
        output.seek(0)
        return send_file(output, 
                         download_name=f"Report_{sess.name}.xlsx",
                         as_attachment=True,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        print(f"Excel failed: {e}")
        output = io.StringIO()
        df.to_csv(output, index=False)
        mem = io.BytesIO()
        mem.write(output.getvalue().encode('utf-8'))
        mem.seek(0)
        return send_file(mem,
                         download_name=f"Report_{sess.name}.csv",
                         as_attachment=True,
                         mimetype='text/csv')
@app.route('/cupper/evaluate/<int:ss_id>', methods=['GET', 'POST'])
@login_required
def cupping(ss_id):
    if current_user.role not in ['Admin', 'Cupper']: return "Access Denied", 403
    ss = SessionSample.query.get_or_404(ss_id)
    
    # Strictly enforce: No evaluation after closing
    if ss.cupping_session.status != 'Open':
        flash('This session is closed and can no longer be evaluated.')
        return redirect(url_for('index'))
        
    # Secure Assignment Check (Server-side)
    if ss.assigned_cupper_id and ss.assigned_cupper_id != current_user.id and current_user.role != 'Admin':
        flash('Access Restricted: This sample is assigned to another professional cupper.')
        return redirect(url_for('index'))
    if request.method == 'POST':
        eval = SensoryEvaluation(
            session_sample_id=ss_id,
            cupper_id=current_user.id,
            aroma=request.form.get('aroma'),
            flavor=request.form.get('flavor'),
            acidity=request.form.get('acidity'),
            body=request.form.get('body'),
            sweetness=request.form.get('sweetness'),
            balance=request.form.get('balance'),
            clean_cup=request.form.get('clean_cup'),
            overall=request.form.get('overall'),
            uniformity=request.form.get('uniformity'),
            defects=request.form.get('defects'),
            notes=request.form.get('notes')
        )
        db.session.add(eval)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('cupping_form.html', ss=ss, t=get_translations(session['lang']))

# --- Init DB ---
def init_data():
    with app.app_context():
        db.create_all()
        if not User.query.first():
            # Only create the first admin if the database is brand new and empty
            hashed = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            db.session.add(User(
                username='admin', 
                email='admin@shibam.com', 
                password_hash=hashed, 
                full_name='System Admin', 
                role='Admin', 
                is_active=True
            ))
            db.session.commit()
            print("INFO: Initial admin user created.")

# Ensure DB and Admin exist on first run (works for both Local and Render)
try:
    init_data()
except Exception as e:
    print(f"Error initializing data: {e}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # In production, host must be 0.0.0.0
    app.run(host='0.0.0.0', port=port)
