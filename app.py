from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import random
import datetime
import os
import re
import json
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
app.config['DATABASE'] = 'securepay.db'

# Advanced AI Features

def analyze_user_behavior(user_id):
    """
    AI-powered user behavior analysis
    Returns behavior profile and anomaly score
    """
    db = get_db()
    
    # Get user transaction history
    transactions = db.execute("""
        SELECT amount, created_at, transaction_type, status
        FROM transactions
        WHERE sender_id = ? OR receiver_id = ?
        ORDER BY created_at DESC
        LIMIT 50
    """, (user_id, user_id)).fetchall()
    
    if not transactions:
        return {'is_new_user': True, 'risk_level': 'MEDIUM'}
    
    amounts = [t['amount'] for t in transactions]
    
    # Calculate behavior metrics
    avg_transaction = sum(amounts) / len(amounts) if amounts else 0
    max_transaction = max(amounts) if amounts else 0
    transaction_count = len(transactions)
    
    # Calculate transaction frequency
    if len(transactions) > 1:
        first_txn = datetime.datetime.strptime(transactions[-1]['created_at'], '%Y-%m-%d %H:%M:%S')
        last_txn = datetime.datetime.strptime(transactions[0]['created_at'], '%Y-%m-%d %H:%M:%S')
        days_active = (last_txn - first_txn).days or 1
        txn_per_day = transaction_count / days_active
    else:
        txn_per_day = 1
    
    # Time pattern analysis
    hours = []
    for t in transactions:
        dt = datetime.datetime.strptime(t['created_at'], '%Y-%m-%d %H:%M:%S')
        hours.append(dt.hour)
    
    night_txns = len([h for h in hours if 0 <= h <= 5])
    night_ratio = night_txns / len(hours) if hours else 0
    
    return {
        'avg_transaction': avg_transaction,
        'max_transaction': max_transaction,
        'transaction_count': transaction_count,
        'txn_per_day': txn_per_day,
        'night_transaction_ratio': night_ratio,
        'is_new_user': False,
        'is_suspicious': txn_per_day > 10 or night_ratio > 0.3
    }

def predict_transaction_legitimacy(transaction_data, user_behavior):
    """
    ML-based prediction of transaction legitimacy
    Uses behavior patterns to predict if transaction is legitimate
    """
    score = 100  # Start with 100% legitimate
    prediction_factors = []
    
    amount = transaction_data.get('amount', 0)
    
    # Factor 1: Amount deviation from user's normal behavior
    if not user_behavior['is_new_user']:
        avg = user_behavior['avg_transaction']
        if avg > 0:
            deviation = abs(amount - avg) / avg
            if deviation > 2:  # More than 200% deviation
                score -= 25
                prediction_factors.append(f"Amount {int(deviation*100)}% above normal behavior")
            elif deviation > 5:
                score -= 40
                prediction_factors.append(f"Amount {int(deviation*100)}% extremely abnormal")
    
    # Factor 2: Frequency pattern
    if user_behavior.get('txn_per_day', 0) > 10:
        score -= 20
        prediction_factors.append("Unusually high transaction frequency")
    
    # Factor 3: Night transaction pattern
    if user_behavior.get('night_transaction_ratio', 0) > 0.3:
        score -= 15
        prediction_factors.append("High proportion of night transactions")
    
    return {
        'legitimacy_score': max(score, 0),
        'is_legitimate': score >= 60,
        'prediction_factors': prediction_factors
    }

def detect_anomaly_patterns(user_id):
    """
    Advanced anomaly detection using statistical analysis
    """
    db = get_db()
    
    # Get recent transaction patterns
    recent_txns = db.execute("""
        SELECT amount, created_at, receiver_id
        FROM transactions
        WHERE sender_id = ? AND created_at > datetime('now', '-7 days')
        ORDER BY created_at DESC
    """, (user_id,)).fetchall()
    
    anomalies = []
    
    if len(recent_txns) > 5:
        amounts = [t['amount'] for t in recent_txns]
        avg = sum(amounts) / len(amounts)
        
        # Standard deviation calculation
        variance = sum((x - avg) ** 2 for x in amounts) / len(amounts)
        std_dev = variance ** 0.5
        
        # Check for outliers (3 standard deviations)
        for txn in recent_txns[:3]:  # Check last 3 transactions
            if abs(txn['amount'] - avg) > 3 * std_dev:
                anomalies.append({
                    'type': 'amount_outlier',
                    'severity': 'HIGH',
                    'detail': f"Amount ₹{txn['amount']} is {abs(txn['amount'] - avg) / std_dev:.1f}σ from mean"
                })
    
    # Check for same-receiver spam
    if len(recent_txns) >= 3:
        receiver_counts = defaultdict(int)
        for txn in recent_txns[:5]:
            if txn['receiver_id']:
                receiver_counts[txn['receiver_id']] += 1
        
        for receiver, count in receiver_counts.items():
            if count >= 3:
                anomalies.append({
                    'type': 'repeated_receiver',
                    'severity': 'MEDIUM',
                    'detail': f"Sent to same receiver {count} times in 7 days"
                })
    
    return anomalies

def ai_risk_assessment(transaction_data):
    """
    Comprehensive AI risk assessment combining multiple AI models
    """
    sender_id = transaction_data.get('sender_id')
    
    # Get user behavior profile
    behavior = analyze_user_behavior(sender_id)
    
    # Predict legitimacy
    legitimacy = predict_transaction_legitimacy(transaction_data, behavior)
    
    # Detect anomalies
    anomalies = detect_anomaly_patterns(sender_id)
    
    # Calculate combined AI score
    ai_score = legitimacy['legitimacy_score']
    
    # Reduce score based on anomalies
    for anomaly in anomalies:
        if anomaly['severity'] == 'HIGH':
            ai_score -= 20
        elif anomaly['severity'] == 'MEDIUM':
            ai_score -= 10
    
    return {
        'ai_legitimacy_score': max(ai_score, 0),
        'user_behavior': behavior,
        'anomalies': anomalies,
        'prediction_factors': legitimacy['prediction_factors'],
        'ai_verdict': 'SAFE' if ai_score >= 70 else ('SUSPICIOUS' if ai_score >= 40 else 'DANGEROUS')
    }

# AI Fraud Detection System
def detect_fraud(transaction_data):
    """
    AI-powered fraud detection using multiple risk factors
    Returns: (is_fraud, risk_score, reasons)
    """
    risk_score = 0
    risk_factors = []
    
    amount = transaction_data.get('amount', 0)
    sender_id = transaction_data.get('sender_id')
    receiver_id = transaction_data.get('receiver_id')
    
    db = get_db()
    
    # === ADVANCED AI ANALYSIS ===
    ai_assessment = ai_risk_assessment(transaction_data)
    
    # AI legitimacy check
    if ai_assessment['ai_legitimacy_score'] < 40:
        risk_score += 30
        risk_factors.append(f"AI legitimacy score low: {ai_assessment['ai_legitimacy_score']}%")
    
    # Add anomaly-based risk
    for anomaly in ai_assessment['anomalies']:
        if anomaly['severity'] == 'HIGH':
            risk_score += 25
            risk_factors.append(f"Anomaly detected: {anomaly['detail']}")
        elif anomaly['severity'] == 'MEDIUM':
            risk_score += 15
            risk_factors.append(f"Pattern alert: {anomaly['detail']}")
    
    # Factor 1: Unusual amount detection
    if amount > 50000:
        risk_score += 30
        risk_factors.append("High transaction amount (>₹50,000)")
    if amount > 100000:
        risk_score += 50
        risk_factors.append("Very high transaction amount (>₹1,00,000)")
    
    # Factor 2: Rapid successive transactions
    recent_txns = db.execute("""
        SELECT COUNT(*) as count FROM transactions 
        WHERE sender_id = ? AND created_at > datetime('now', '-5 minutes')
    """, (sender_id,)).fetchone()
    
    if recent_txns['count'] > 3:
        risk_score += 25
        risk_factors.append(f"Multiple transactions in short time ({recent_txns['count']} in 5 min)")
    
    # Factor 3: New account activity
    sender = db.execute("SELECT created_at FROM users WHERE id = ?", (sender_id,)).fetchone()
    account_age_hours = (datetime.datetime.now() - datetime.datetime.strptime(sender['created_at'], '%Y-%m-%d %H:%M:%S')).total_seconds() / 3600
    
    if account_age_hours < 24 and amount > 10000:
        risk_score += 35
        risk_factors.append("New account with high-value transaction")
    
    # Factor 4: Velocity check (total amount in last hour)
    hourly_total = db.execute("""
        SELECT COALESCE(SUM(amount), 0) as total FROM transactions 
        WHERE sender_id = ? AND created_at > datetime('now', '-1 hour')
    """, (sender_id,)).fetchone()
    
    if hourly_total['total'] > 100000:
        risk_score += 40
        risk_factors.append(f"High transaction velocity (₹{hourly_total['total']:.2f} in 1 hour)")
    
    # Factor 5: Round number detection (common in fraud)
    if amount % 10000 == 0 and amount >= 50000:
        risk_score += 15
        risk_factors.append("Suspicious round number amount")
    
    # Factor 6: Different receiver each time
    unique_receivers = db.execute("""
        SELECT COUNT(DISTINCT receiver_id) as count FROM transactions 
        WHERE sender_id = ? AND created_at > datetime('now', '-1 day')
    """, (sender_id,)).fetchone()
    
    if unique_receivers['count'] > 5:
        risk_score += 20
        risk_factors.append(f"Multiple different receivers ({unique_receivers['count']} in 24h)")
    
    # Factor 7: Time-based anomaly (unusual hours)
    current_hour = datetime.datetime.now().hour
    if current_hour >= 0 and current_hour <= 5:  # Late night transactions
        risk_score += 15
        risk_factors.append("Transaction during unusual hours (12 AM - 5 AM)")
    
    # Factor 8: Pattern matching - suspicious keywords in description
    description = transaction_data.get('description', '').lower()
    suspicious_keywords = ['urgent', 'emergency', 'immediately', 'lottery', 'prize', 'won', 'claim']
    for keyword in suspicious_keywords:
        if keyword in description:
            risk_score += 10
            risk_factors.append(f"Suspicious keyword detected: '{keyword}'")
            break
    
    # Determine fraud status
    is_fraud = risk_score >= 60  # Threshold for blocking
    is_suspicious = risk_score >= 40  # Threshold for flagging
    
    return {
        'is_fraud': is_fraud,
        'is_suspicious': is_suspicious,
        'risk_score': min(risk_score, 100),  # Cap at 100
        'risk_factors': risk_factors,
        'risk_level': 'HIGH' if is_fraud else ('MEDIUM' if is_suspicious else 'LOW'),
        'ai_assessment': ai_assessment
    }

# Database initialization
def init_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mobile TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT,
        upi_id TEXT UNIQUE,
        balance REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active INTEGER DEFAULT 1
    )''')
    
    # Merchants table
    c.execute('''CREATE TABLE IF NOT EXISTS merchants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        merchant_name TEXT NOT NULL,
        merchant_id TEXT UNIQUE NOT NULL,
        mobile TEXT NOT NULL,
        email TEXT,
        category TEXT,
        balance REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active INTEGER DEFAULT 1
    )''')
    
    # Transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id TEXT UNIQUE NOT NULL,
        sender_id INTEGER,
        receiver_id INTEGER,
        merchant_id INTEGER,
        amount REAL NOT NULL,
        transaction_type TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users (id),
        FOREIGN KEY (receiver_id) REFERENCES users (id),
        FOREIGN KEY (merchant_id) REFERENCES merchants (id)
    )''')
    
    # Admin table
    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # OTP table
    c.execute('''CREATE TABLE IF NOT EXISTS otp_verification (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mobile TEXT NOT NULL,
        otp TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        is_used INTEGER DEFAULT 0
    )''')
    
    # Create default admin if doesn't exist
    c.execute("SELECT * FROM admins WHERE username = 'admin'")
    if not c.fetchone():
        admin_password = generate_password_hash('admin123')
        c.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)", 
                 ('admin', admin_password))
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Helper functions
def generate_otp():
    return str(random.randint(100000, 999999))

def generate_transaction_id():
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    random_num = random.randint(1000, 9999)
    return f"TXN{timestamp}{random_num}"

def generate_merchant_id():
    timestamp = datetime.datetime.now().strftime('%Y%m%d')
    random_num = random.randint(10000, 99999)
    return f"MER{timestamp}{random_num}"

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        mobile = request.form.get('mobile')
        
        if not mobile or len(mobile) != 10:
            flash('Please enter a valid 10-digit mobile number', 'error')
            return render_template('user_login.html')
        
        # Generate OTP
        otp = generate_otp()
        expires_at = datetime.datetime.now() + datetime.timedelta(minutes=5)
        
        db = get_db()
        db.execute("INSERT INTO otp_verification (mobile, otp, expires_at) VALUES (?, ?, ?)",
                  (mobile, otp, expires_at))
        db.commit()
        
        # In production, send OTP via SMS
        flash(f'OTP sent to {mobile}. Demo OTP: {otp}', 'success')
        session['verify_mobile'] = mobile
        
        return redirect(url_for('verify_otp'))
    
    return render_template('user_login.html')

@app.route('/user/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'verify_mobile' not in session:
        return redirect(url_for('user_login'))
    
    if request.method == 'POST':
        otp = request.form.get('otp')
        mobile = session.get('verify_mobile')
        
        db = get_db()
        result = db.execute("""
            SELECT * FROM otp_verification 
            WHERE mobile = ? AND otp = ? AND is_used = 0 AND expires_at > ? 
            ORDER BY created_at DESC LIMIT 1
        """, (mobile, otp, datetime.datetime.now())).fetchone()
        
        if result:
            # Mark OTP as used
            db.execute("UPDATE otp_verification SET is_used = 1 WHERE id = ?", (result['id'],))
            db.commit()
            
            # Check if user exists
            user = db.execute("SELECT * FROM users WHERE mobile = ?", (mobile,)).fetchone()
            
            if not user:
                # Create new user
                cursor = db.execute("INSERT INTO users (mobile, name, upi_id) VALUES (?, ?, ?)",
                          (mobile, f"User_{mobile}", f"{mobile}@securepay"))
                db.commit()
                user_id = cursor.lastrowid
            else:
                user_id = user['id']
            
            session['user_id'] = user_id
            session['user_mobile'] = mobile
            session.pop('verify_mobile', None)
            
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid or expired OTP', 'error')
    
    return render_template('verify_otp.html')

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    
    # Get recent transactions
    transactions = db.execute("""
        SELECT t.*, 
               CASE 
                   WHEN t.sender_id = ? THEN 'debit'
                   ELSE 'credit'
               END as type,
               CASE 
                   WHEN t.sender_id = ? THEN u2.name
                   ELSE u1.name
               END as other_party
        FROM transactions t
        LEFT JOIN users u1 ON t.sender_id = u1.id
        LEFT JOIN users u2 ON t.receiver_id = u2.id
        WHERE (t.sender_id = ? OR t.receiver_id = ?) AND t.status = 'completed'
        ORDER BY t.created_at DESC LIMIT 10
    """, (session['user_id'], session['user_id'], session['user_id'], session['user_id'])).fetchall()
    
    # AI-powered spending insights
    insights = get_ai_insights(session['user_id'])
    
    return render_template('user_dashboard.html', user=user, transactions=transactions, insights=insights)

def get_ai_insights(user_id):
    """Generate AI-powered insights for user"""
    db = get_db()
    
    # Get transaction history
    txns = db.execute("""
        SELECT amount, created_at, transaction_type
        FROM transactions
        WHERE sender_id = ? AND status = 'completed'
        AND created_at > datetime('now', '-30 days')
        ORDER BY created_at DESC
    """, (user_id,)).fetchall()
    
    if not txns:
        return None
    
    total_spent = sum(t['amount'] for t in txns)
    avg_transaction = total_spent / len(txns) if txns else 0
    
    # Trend analysis
    recent_7_days = [t for t in txns if (datetime.datetime.now() - datetime.datetime.strptime(t['created_at'], '%Y-%m-%d %H:%M:%S')).days <= 7]
    prev_7_days = [t for t in txns if 7 < (datetime.datetime.now() - datetime.datetime.strptime(t['created_at'], '%Y-%m-%d %H:%M:%S')).days <= 14]
    
    recent_spent = sum(t['amount'] for t in recent_7_days)
    prev_spent = sum(t['amount'] for t in prev_7_days) if prev_7_days else 1
    
    trend = ((recent_spent - prev_spent) / prev_spent * 100) if prev_spent > 0 else 0
    
    # AI recommendations
    recommendations = []
    if total_spent > 50000:
        recommendations.append("💡 You've spent ₹{:.0f} this month. Consider setting a budget limit.".format(total_spent))
    if trend > 50:
        recommendations.append("📈 Your spending increased {}% this week. Review your transactions.".format(int(trend)))
    if avg_transaction > 10000:
        recommendations.append("💰 Your average transaction is ₹{:.0f}. Enable 2FA for large amounts.".format(avg_transaction))
    
    return {
        'total_spent_month': total_spent,
        'transaction_count': len(txns),
        'avg_transaction': avg_transaction,
        'spending_trend': trend,
        'recommendations': recommendations
    }

@app.route('/user/insights')
@login_required
def user_insights():
    """AI-powered transaction insights and analytics"""
    db = get_db()
    user_id = session['user_id']
    
    # Get comprehensive analytics
    analytics = get_comprehensive_analytics(user_id)
    
    return render_template('user_insights.html', analytics=analytics)

def get_comprehensive_analytics(user_id):
    """Generate comprehensive AI analytics"""
    db = get_db()
    
    # Get all transactions
    all_txns = db.execute("""
        SELECT t.*, u.name as receiver_name
        FROM transactions t
        LEFT JOIN users u ON t.receiver_id = u.id
        WHERE t.sender_id = ? AND t.status = 'completed'
        ORDER BY t.created_at DESC
    """, (user_id,)).fetchall()
    
    if not all_txns:
        return {'has_data': False}
    
    # Calculate metrics
    total_sent = sum(t['amount'] for t in all_txns)
    total_transactions = len(all_txns)
    
    # Top receivers
    receiver_totals = defaultdict(lambda: {'name': '', 'amount': 0, 'count': 0})
    for t in all_txns:
        if t['receiver_name']:
            receiver_totals[t['receiver_name']]['name'] = t['receiver_name']
            receiver_totals[t['receiver_name']]['amount'] += t['amount']
            receiver_totals[t['receiver_name']]['count'] += 1
    
    top_receivers = sorted(receiver_totals.values(), key=lambda x: x['amount'], reverse=True)[:5]
    
    # Spending by time of day
    hour_spending = defaultdict(float)
    for t in all_txns:
        dt = datetime.datetime.strptime(t['created_at'], '%Y-%m-%d %H:%M:%S')
        hour_spending[dt.hour] += t['amount']
    
    peak_hour = max(hour_spending.items(), key=lambda x: x[1])[0] if hour_spending else 12
    
    # Monthly trend
    monthly_spending = defaultdict(float)
    for t in all_txns:
        dt = datetime.datetime.strptime(t['created_at'], '%Y-%m-%d %H:%M:%S')
        month_key = dt.strftime('%Y-%m')
        monthly_spending[month_key] += t['amount']
    
    return {
        'has_data': True,
        'total_sent': total_sent,
        'total_transactions': total_transactions,
        'avg_transaction': total_sent / total_transactions,
        'top_receivers': top_receivers,
        'peak_spending_hour': peak_hour,
        'monthly_trend': dict(sorted(monthly_spending.items()))
    }

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = get_db()
        admin = db.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
        
        if admin and check_password_hash(admin['password_hash'], password):
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    db = get_db()
    
    # Get statistics
    total_users = db.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
    total_merchants = db.execute("SELECT COUNT(*) as count FROM merchants").fetchone()['count']
    total_transactions = db.execute("SELECT COUNT(*) as count FROM transactions").fetchone()['count']
    total_volume = db.execute("SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE status = 'completed'").fetchone()['total']
    
    return render_template('admin_dashboard.html', 
                         total_users=total_users,
                         total_merchants=total_merchants,
                         total_transactions=total_transactions,
                         total_volume=total_volume)

@app.route('/admin/users')
@admin_required
def view_users():
    db = get_db()
    users = db.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    return render_template('admin_users.html', users=users)

@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    db = get_db()
    
    # Get user info before deletion
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('view_users'))
    
    # Delete user's transactions
    db.execute("DELETE FROM transactions WHERE sender_id = ? OR receiver_id = ?", (user_id, user_id))
    
    # Delete user
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    
    flash(f'User {user["name"]} (ID: {user_id}) deleted successfully along with all transactions', 'success')
    return redirect(url_for('view_users'))

@app.route('/admin/delete-merchant/<int:merchant_id>', methods=['POST'])
@admin_required
def delete_merchant(merchant_id):
    db = get_db()
    
    # Get merchant info before deletion
    merchant = db.execute("SELECT * FROM merchants WHERE id = ?", (merchant_id,)).fetchone()
    
    if not merchant:
        flash('Merchant not found', 'error')
        return redirect(url_for('view_merchants'))
    
    # Delete merchant's transactions
    db.execute("DELETE FROM transactions WHERE merchant_id = ?", (merchant_id,))
    
    # Delete merchant
    db.execute("DELETE FROM merchants WHERE id = ?", (merchant_id,))
    db.commit()
    
    flash(f'Merchant {merchant["merchant_name"]} deleted successfully', 'success')
    return redirect(url_for('view_merchants'))

@app.route('/admin/fraud-monitor')
@admin_required
def fraud_monitor():
    db = get_db()
    
    # Get blocked transactions
    blocked = db.execute("""
        SELECT t.*, u1.name as sender_name, u2.name as receiver_name 
        FROM transactions t
        LEFT JOIN users u1 ON t.sender_id = u1.id
        LEFT JOIN users u2 ON t.receiver_id = u2.id
        WHERE t.status = 'blocked'
        ORDER BY t.created_at DESC
    """).fetchall()
    
    # Get flagged transactions
    flagged = db.execute("""
        SELECT t.*, u1.name as sender_name, u2.name as receiver_name 
        FROM transactions t
        LEFT JOIN users u1 ON t.sender_id = u1.id
        LEFT JOIN users u2 ON t.receiver_id = u2.id
        WHERE t.status = 'flagged'
        ORDER BY t.created_at DESC
    """).fetchall()
    
    # Get high-risk users (users with blocked/flagged transactions)
    high_risk_users = db.execute("""
        SELECT u.*, 
               COUNT(CASE WHEN t.status = 'blocked' THEN 1 END) as blocked_count,
               COUNT(CASE WHEN t.status = 'flagged' THEN 1 END) as flagged_count
        FROM users u
        LEFT JOIN transactions t ON u.id = t.sender_id
        GROUP BY u.id
        HAVING blocked_count > 0 OR flagged_count > 0
        ORDER BY blocked_count DESC, flagged_count DESC
    """).fetchall()
    
    return render_template('admin_fraud_monitor.html', 
                         blocked=blocked, 
                         flagged=flagged,
                         high_risk_users=high_risk_users)

@app.route('/admin/merchants')
@admin_required
def view_merchants():
    db = get_db()
    merchants = db.execute("SELECT * FROM merchants ORDER BY created_at DESC").fetchall()
    return render_template('admin_merchants.html', merchants=merchants)

@app.route('/admin/transactions')
@admin_required
def view_transactions():
    db = get_db()
    transactions = db.execute("""
        SELECT t.*, u1.name as sender_name, u2.name as receiver_name, m.merchant_name
        FROM transactions t
        LEFT JOIN users u1 ON t.sender_id = u1.id
        LEFT JOIN users u2 ON t.receiver_id = u2.id
        LEFT JOIN merchants m ON t.merchant_id = m.id
        ORDER BY t.created_at DESC
    """).fetchall()
    return render_template('admin_transactions.html', transactions=transactions)

@app.route('/admin/create-account', methods=['GET', 'POST'])
@admin_required
def create_account():
    if request.method == 'POST':
        account_type = request.form.get('account_type')
        db = get_db()
        
        if account_type == 'user':
            mobile = request.form.get('mobile')
            name = request.form.get('name')
            email = request.form.get('email')
            upi_id = request.form.get('upi_id') or f"{mobile}@securepay"
            
            try:
                db.execute("INSERT INTO users (mobile, name, email, upi_id) VALUES (?, ?, ?, ?)",
                          (mobile, name, email, upi_id))
                db.commit()
                flash(f'User account created successfully for {name}', 'success')
            except sqlite3.IntegrityError:
                flash('User with this mobile or UPI ID already exists', 'error')
        
        elif account_type == 'merchant':
            merchant_name = request.form.get('merchant_name')
            mobile = request.form.get('mobile')
            email = request.form.get('email')
            category = request.form.get('category')
            merchant_id = generate_merchant_id()
            
            try:
                db.execute("INSERT INTO merchants (merchant_name, merchant_id, mobile, email, category) VALUES (?, ?, ?, ?, ?)",
                          (merchant_name, merchant_id, mobile, email, category))
                db.commit()
                flash(f'Merchant account created successfully. Merchant ID: {merchant_id}', 'success')
            except sqlite3.IntegrityError:
                flash('Merchant with this ID already exists', 'error')
        
        return redirect(url_for('create_account'))
    
    return render_template('admin_create_account.html')

@app.route('/user/add-money', methods=['GET', 'POST'])
@login_required
def add_money():
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        
        if amount <= 0:
            flash('Please enter a valid amount', 'error')
            return redirect(url_for('add_money'))
        
        db = get_db()
        
        # Update user balance
        db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", 
                  (amount, session['user_id']))
        
        # Create transaction record
        transaction_id = generate_transaction_id()
        db.execute("""INSERT INTO transactions 
                     (transaction_id, receiver_id, amount, transaction_type, status, description) 
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (transaction_id, session['user_id'], amount, 'credit', 'completed', 'Money added to wallet'))
        db.commit()
        
        flash(f'₹{amount} added successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    
    return render_template('add_money.html')

@app.route('/user/send-money', methods=['GET', 'POST'])
@login_required
def send_money():
    if request.method == 'POST':
        receiver_upi = request.form.get('receiver_upi')
        amount = float(request.form.get('amount'))
        description = request.form.get('description', 'Money transfer')
        
        if amount <= 0:
            flash('Please enter a valid amount', 'error')
            return redirect(url_for('send_money'))
        
        db = get_db()
        
        # Get sender details
        sender = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        
        # Check balance
        if sender['balance'] < amount:
            flash('Insufficient balance', 'error')
            return redirect(url_for('send_money'))
        
        # Get receiver details
        receiver = db.execute("SELECT * FROM users WHERE upi_id = ?", (receiver_upi,)).fetchone()
        
        if not receiver:
            flash('Receiver UPI ID not found', 'error')
            return redirect(url_for('send_money'))
        
        if receiver['id'] == session['user_id']:
            flash('Cannot send money to yourself', 'error')
            return redirect(url_for('send_money'))
        
        # AI FRAUD DETECTION
        fraud_check = detect_fraud({
            'amount': amount,
            'sender_id': session['user_id'],
            'receiver_id': receiver['id'],
            'description': description
        })
        
        # Block if high fraud risk
        if fraud_check['is_fraud']:
            transaction_id = generate_transaction_id()
            # Log blocked transaction
            db.execute("""INSERT INTO transactions 
                         (transaction_id, sender_id, receiver_id, amount, transaction_type, status, description) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)""",
                      (transaction_id, session['user_id'], receiver['id'], amount, 'transfer', 'blocked', 
                       f"FRAUD DETECTED - {description}"))
            db.commit()
            
            flash(f'⚠️ Transaction blocked! Fraud risk detected (Risk Score: {fraud_check["risk_score"]}%). Reasons: {", ".join(fraud_check["risk_factors"])}', 'error')
            return redirect(url_for('send_money'))
        
        # Flag if suspicious
        status = 'flagged' if fraud_check['is_suspicious'] else 'completed'
        
        # Process transaction
        db.execute("UPDATE users SET balance = balance - ? WHERE id = ?", 
                  (amount, session['user_id']))
        db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", 
                  (amount, receiver['id']))
        
        # Create transaction record with fraud info
        transaction_id = generate_transaction_id()
        fraud_info = f"Risk: {fraud_check['risk_level']} ({fraud_check['risk_score']}%)"
        full_description = f"{description} | {fraud_info}"
        
        db.execute("""INSERT INTO transactions 
                     (transaction_id, sender_id, receiver_id, amount, transaction_type, status, description) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (transaction_id, session['user_id'], receiver['id'], amount, 'transfer', status, full_description))
        db.commit()
        
        if fraud_check['is_suspicious']:
            flash(f'⚠️ Transaction completed but flagged for review. Risk Score: {fraud_check["risk_score"]}%', 'error')
        else:
            flash(f'✅ ₹{amount} sent successfully to {receiver["name"]}! (Risk Score: {fraud_check["risk_score"]}% - Safe)', 'success')
        
        return redirect(url_for('user_dashboard'))
    
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    
    return render_template('send_money.html', user=user)

@app.route('/user/request-money', methods=['GET', 'POST'])
@login_required
def request_money():
    if request.method == 'POST':
        requester_upi = request.form.get('requester_upi')
        amount = float(request.form.get('amount'))
        message = request.form.get('message', 'Money request')
        
        if amount <= 0:
            flash('Please enter a valid amount', 'error')
            return redirect(url_for('request_money'))
        
        db = get_db()
        
        # Get current user details
        user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        
        # Get requester details
        requester = db.execute("SELECT * FROM users WHERE upi_id = ?", (requester_upi,)).fetchone()
        
        if not requester:
            flash('User UPI ID not found', 'error')
            return redirect(url_for('request_money'))
        
        if requester['id'] == session['user_id']:
            flash('Cannot request money from yourself', 'error')
            return redirect(url_for('request_money'))
        
        # In a real app, this would create a pending request
        # For demo, we'll just show a success message
        flash(f'Money request of ₹{amount} sent to {requester["name"]}!', 'success')
        return redirect(url_for('user_dashboard'))
    
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    
    return render_template('request_money.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(app.config['DATABASE']):
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
