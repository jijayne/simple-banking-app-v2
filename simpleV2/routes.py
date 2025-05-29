from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import app, csrf
from extensions import db, limiter
from forms import LoginForm, RegistrationForm, TransferForm, ResetPasswordRequestForm, ResetPasswordForm, DepositForm, UserEditForm, ConfirmTransferForm
from models import User, Transaction
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import os
from functools import wraps
import psgc_api
import datetime

# Context processor to provide current year to all templates
@app.context_processor
def inject_year():
    return {'current_year': datetime.datetime.now().year}

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need to be an admin to access this page.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Manager required decorator
def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_manager:
            flash('You need to be a manager to access this page.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Email functionality (simulated for this example)
def send_password_reset_email(user):
    # In a real app, this would send an actual email with a reset token
    # For simplicity, we're just creating the token and displaying it
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = serializer.dumps(user.email, salt='password-reset')
    reset_url = url_for('reset_password', token=token, _external=True)
    flash(f'Password reset link (would be emailed): {reset_url}')

@app.route('/')
@app.route('/index')
@login_required
def index():
    recent_transactions = current_user.get_recent_transactions(5)
    return render_template('index.html', transactions=recent_transactions)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if user.status == 'active':
                login_user(user)
                next_page = request.args.get('next')
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for('index')
                return redirect(next_page)
            else:
                flash('Your account is not active. Please contact an administrator.')
        else:
            flash('Invalid username or password')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now registered!')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/account')
@login_required
def account():
    recent_transactions = current_user.get_recent_transactions(10)
    return render_template('account.html', transactions=recent_transactions)

@app.route('/transfer', methods=['GET', 'POST'])
@login_required
@limiter.limit("20 per hour")
def transfer():
    form = TransferForm()
    if form.validate_on_submit():
        # Find recipient
        if form.transfer_type.data == 'username':
            recipient = User.query.filter_by(username=form.recipient_username.data).first()
        else:
            recipient = User.query.filter_by(account_number=form.recipient_account.data).first()
        
        if not recipient:
            flash('Recipient not found')
            return render_template('transfer.html', form=form)
        
        if recipient.id == current_user.id:
            flash('Cannot transfer to yourself')
            return render_template('transfer.html', form=form)
        
        # Store transfer details in session for confirmation
        session['transfer_data'] = {
            'recipient_id': recipient.id,
            'amount': form.amount.data,
            'recipient_name': recipient.display_name
        }
        
        return redirect(url_for('confirm_transfer'))
    
    return render_template('transfer.html', form=form)

@app.route('/confirm_transfer', methods=['GET', 'POST'])
@login_required
def confirm_transfer():
    transfer_data = session.get('transfer_data')
    if not transfer_data:
        flash('No transfer to confirm')
        return redirect(url_for('transfer'))
    
    form = ConfirmTransferForm()
    recipient = User.query.get(transfer_data['recipient_id'])
    
    if form.validate_on_submit():
        if form.confirm.data:
            success, message = current_user.transfer_money(recipient, transfer_data['amount'])
            if success:
                db.session.commit()
                flash(f'Transfer of ${transfer_data["amount"]:.2f} to {recipient.display_name} successful!')
                session.pop('transfer_data', None)
                return redirect(url_for('account'))
            else:
                flash(f'Transfer failed: {message}')
        else:
            session.pop('transfer_data', None)
            flash('Transfer cancelled')
            return redirect(url_for('transfer'))
    
    return render_template('confirm_transfer.html', form=form, transfer_data=transfer_data, recipient=recipient)

@app.route('/execute_transfer', methods=['POST'])
@login_required
@limiter.limit("20 per hour")
def execute_transfer():
    # This route is for AJAX transfers if needed
    return jsonify({'status': 'success'})

@app.route('/reset_password_request', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    
    return render_template('reset_password_request.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset', max_age=3600)
    except SignatureExpired:
        flash('The password reset token has expired.')
        return redirect(url_for('reset_password_request'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return redirect(url_for('index'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', form=form)

# Admin routes
@app.route('/admin')
@login_required
@admin_required
@limiter.limit("60 per hour")
def admin_dashboard():
    users = User.query.all()
    return render_template('admin/dashboard.html', users=users)

@app.route('/admin/activate_user/<int:user_id>')
@login_required
@admin_required
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.activate_account()
    db.session.commit()
    flash(f'User {user.username} has been activated.')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/deactivate_user/<int:user_id>')
@login_required
@admin_required
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.deactivate_account()
    db.session.commit()
    flash(f'User {user.username} has been deactivated.')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/create_account', methods=['GET', 'POST'])
@login_required
@admin_required
@limiter.limit("20 per hour")
def create_account():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, status='active')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {user.username}')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/create_account.html', form=form)

@app.route('/admin/deposit', methods=['GET', 'POST'])
@login_required
@admin_required
@limiter.limit("30 per hour")
def admin_deposit():
    form = DepositForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            success, message = user.deposit(form.amount.data, current_user)
            if success:
                db.session.commit()
                flash(f'Deposited ${form.amount.data:.2f} to {user.username}')
            else:
                flash(f'Deposit failed: {message}')
        else:
            flash('User not found')
    
    return render_template('admin/deposit.html', form=form)

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash(f'User {user.username} updated successfully')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_user.html', form=form, user=user)

# Apply rate limiting to API endpoints
@app.route('/api/provinces/<region_code>')
@login_required
@admin_required
@limiter.limit("30 per minute")
def api_provinces(region_code):
    provinces = psgc_api.get_provinces(region_code)
    return jsonify(provinces)

@app.route('/api/cities/<province_code>')
@login_required
@admin_required
@limiter.limit("30 per minute")
def api_cities(province_code):
    cities = psgc_api.get_cities(province_code)
    return jsonify(cities)

@app.route('/api/barangays/<city_code>')
@login_required
@admin_required
@limiter.limit("30 per minute")
def api_barangays(city_code):
    barangays = psgc_api.get_barangays(city_code=city_code)
    return jsonify(barangays)

# Manager routes
@app.route('/manager')
@login_required
@manager_required
@limiter.limit("60 per hour")
def manager_dashboard():
    users = User.query.all()
    admins = User.query.filter_by(is_admin=True).all()
    return render_template('manager/dashboard.html', users=users, admins=admins)

@app.route('/manager/create_admin', methods=['GET', 'POST'])
@login_required
@manager_required
@limiter.limit("10 per hour")
def create_admin():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, status='active', is_admin=True)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Admin account created for {user.username}')
        return redirect(url_for('manager_dashboard'))
    
    return render_template('manager/create_admin.html', form=form)

@app.route('/manager/toggle_admin/<int:user_id>')
@login_required
@manager_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin privileges {status} for {user.username}')
    return redirect(url_for('manager_dashboard'))

@app.route('/manager/user_list')
@login_required
@manager_required
def manager_user_list():
    users = User.query.filter_by(is_admin=False, is_manager=False).all()
    return render_template('manager/user_list.html', users=users)

@app.route('/manager/admin_list')
@login_required
@manager_required
def manager_admin_list():
    admins = User.query.filter_by(is_admin=True).all()
    return render_template('manager/admin_list.html', admins=admins)

@app.route('/manager/admin_transactions')
@login_required
@manager_required
def admin_transactions():
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(100).all()
    return render_template('manager/admin_transactions.html', transactions=transactions)

@app.route('/manager/transfers')
@login_required
@manager_required
def manager_transfers():
    # Base query - only get transfer transactions
    query = Transaction.query.filter(Transaction.transaction_type == 'transfer')
    
    # Apply search if provided
    search_term = request.args.get('search', '').strip()
    if search_term:
        # Build list of transaction IDs that match search criteria
        matching_transaction_ids = []
        
        # If search term is a number, check transaction ID
        if search_term.isdigit():
            matching_transaction_ids.extend([t.id for t in Transaction.query.filter(Transaction.id == int(search_term)).all()])
        
        # Search by sender username
        sender_matches = Transaction.query.join(
            User, Transaction.sender_id == User.id
        ).filter(
            User.username.ilike(f'%{search_term}%')
        ).all()
        matching_transaction_ids.extend([t.id for t in sender_matches])
        
        # Search by receiver username
        receiver_matches = Transaction.query.join(
            User, Transaction.receiver_id == User.id
        ).filter(
            User.username.ilike(f'%{search_term}%')
        ).all()
        matching_transaction_ids.extend([t.id for t in receiver_matches])
        
        # Search by sender account number
        sender_account_matches = Transaction.query.join(
            User, Transaction.sender_id == User.id
        ).filter(
            User.account_number.ilike(f'%{search_term}%')
        ).all()
        matching_transaction_ids.extend([t.id for t in sender_account_matches])
        
        # Search by receiver account number
        receiver_account_matches = Transaction.query.join(
            User, Transaction.receiver_id == User.id
        ).filter(
            User.account_number.ilike(f'%{search_term}%')
        ).all()
        matching_transaction_ids.extend([t.id for t in receiver_account_matches])
        
        # Search by amount (if search term can be converted to float)
        try:
            amount = float(search_term)
            amount_matches = Transaction.query.filter(Transaction.amount == amount).all()
            matching_transaction_ids.extend([t.id for t in amount_matches])
        except ValueError:
            pass
            
        # Filter original query to only include matching transactions
        if matching_transaction_ids:
            query = query.filter(Transaction.id.in_(set(matching_transaction_ids)))
        else:
            # If no matches, return empty result
            query = query.filter(Transaction.id == -1)  # Impossible condition to return empty set
    
    # Apply date range filter if provided
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    if from_date:
        try:
            from_datetime = datetime.datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(Transaction.timestamp >= from_datetime)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_datetime = datetime.datetime.strptime(to_date, '%Y-%m-%d')
            # Add one day to include the entire end date
            to_datetime = to_datetime + datetime.timedelta(days=1)
            query = query.filter(Transaction.timestamp < to_datetime)
        except ValueError:
            pass
    
    # Apply amount range filter if provided
    min_amount = request.args.get('min_amount')
    max_amount = request.args.get('max_amount')
    
    if min_amount:
        try:
            min_amount_value = float(min_amount)
            query = query.filter(Transaction.amount >= min_amount_value)
        except ValueError:
            pass
    
    if max_amount:
        try:
            max_amount_value = float(max_amount)
            query = query.filter(Transaction.amount <= max_amount_value)
        except ValueError:
            pass
    
    # Apply user filter if provided
    user_id = request.args.get('user_id')
    user_role = request.args.get('user_role')
    
    if user_id and not user_id.isdigit():
        flash('Invalid user ID filter.')
        return redirect(url_for('manager_transfers'))

    if user_id and user_id.isdigit():
        user_id = int(user_id)
        if user_role == 'sender':
            query = query.filter(Transaction.sender_id == user_id)
        elif user_role == 'receiver':
            query = query.filter(Transaction.receiver_id == user_id)
        else:
            query = query.filter(
                db.or_(
                    Transaction.sender_id == user_id,
                    Transaction.receiver_id == user_id
                )
            )
    
    # Get all users for filter dropdown
    users = User.query.all()
    
    # Get sorted results
    transactions = query.order_by(Transaction.timestamp.desc()).all()
    
    return render_template('manager/transfers.html', 
                         title='Transfer Transactions', 
                         transactions=transactions,
                         users=users) 
# Error handlers (add at the very end of routes.py)
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500