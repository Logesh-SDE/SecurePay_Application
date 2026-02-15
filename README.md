# SecurePay - UPI Payment System

A complete full-stack web application for secure UPI payments built with Python Flask.

## Features

### User Features
- **OTP-based Authentication**: Secure login with mobile number and OTP verification
- **User Dashboard**: View balance, UPI ID, and transaction history
- **Transaction History**: Track all credit and debit transactions
- **Real-time Balance**: Check account balance instantly

### Admin Features
- **Admin Control Panel**: Centralized dashboard for system management
- **User Management**: View and manage all registered users
- **Merchant Management**: Register and manage merchants
- **Transaction Monitoring**: Audit complete transaction logs
- **Account Creation**: Onboard new users and merchants
- **Statistics Dashboard**: View key metrics and analytics

### Security Features
- Machine learning fraud detection (simulated)
- OTP-based authentication
- Session management
- Secure password hashing for admin accounts
- Input validation and sanitization

## Technology Stack

- **Backend**: Python 3, Flask
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: OTP-based verification
- **Security**: Werkzeug password hashing

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   cd securepay_project
   ```

2. **Install dependencies**
   ```bash
   pip install flask --break-system-packages
   ```

3. **Run the application**
   ```bash
   python3 app.py
   ```

4. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`
   - Or: `http://127.0.0.1:5000`

## Default Credentials

### Admin Login
- **Username**: admin
- **Password**: admin123

### User Login
- Use any 10-digit mobile number
- OTP will be displayed on screen (for demo purposes)
- In production, OTP should be sent via SMS

## Project Structure

```
securepay_project/
├── app.py                      # Main Flask application
├── securepay.db               # SQLite database (auto-created)
├── templates/                 # HTML templates
│   ├── base.html
│   ├── index.html            # Homepage
│   ├── user_login.html       # User login
│   ├── verify_otp.html       # OTP verification
│   ├── admin_login.html      # Admin login
│   ├── admin_dashboard.html  # Admin control panel
│   ├── admin_create_account.html
│   ├── admin_users.html
│   ├── admin_merchants.html
│   ├── admin_transactions.html
│   └── user_dashboard.html
├── static/
│   ├── css/
│   │   └── style.css         # Main stylesheet
│   └── js/
│       └── main.js           # JavaScript functionality
└── README.md
```

## Database Schema

### Users Table
- id, mobile, name, email, upi_id, balance, created_at, is_active

### Merchants Table
- id, merchant_name, merchant_id, mobile, email, category, balance, created_at, is_active

### Transactions Table
- id, transaction_id, sender_id, receiver_id, merchant_id, amount, transaction_type, status, description, created_at

### Admins Table
- id, username, password_hash, created_at

### OTP Verification Table
- id, mobile, otp, created_at, expires_at, is_used

## Key Features Explained

### 1. OTP Authentication
- User enters mobile number
- System generates 6-digit OTP
- OTP valid for 5 minutes
- Secure verification before granting access

### 2. Admin Control Panel
Four main sections:
- **Create Account**: Add new users or merchants
- **View Users**: See all registered bank accounts
- **View Merchants**: Manage merchant accounts
- **View Transactions**: Audit transaction logs

### 3. User Dashboard
- Display current balance
- Show UPI ID
- List recent transactions
- Quick action buttons (Send, Request, Scan QR)

### 4. Transaction Management
- Unique transaction IDs
- Status tracking (pending, completed, failed)
- Complete audit trail
- Real-time balance updates

## API Routes

### Public Routes
- `/` - Homepage
- `/user/login` - User login page
- `/user/verify-otp` - OTP verification
- `/admin/login` - Admin login

### User Routes (Login Required)
- `/user/dashboard` - User dashboard

### Admin Routes (Admin Login Required)
- `/admin/dashboard` - Admin control panel
- `/admin/users` - View all users
- `/admin/merchants` - View all merchants
- `/admin/transactions` - View all transactions
- `/admin/create-account` - Create new accounts

### Common Routes
- `/logout` - Logout (clears session)

## Security Considerations

### Current Implementation (Demo)
- OTP displayed on screen for testing
- Default admin credentials
- SQLite database for simplicity

### Production Recommendations
1. **OTP Delivery**: Integrate SMS gateway (Twilio, AWS SNS, etc.)
2. **Database**: Use PostgreSQL or MySQL
3. **Password Policy**: Enforce strong admin passwords
4. **HTTPS**: Deploy with SSL/TLS certificates
5. **Rate Limiting**: Implement API rate limiting
6. **Session Security**: Use secure session cookies
7. **Input Validation**: Enhanced server-side validation
8. **Logging**: Implement comprehensive logging
9. **Environment Variables**: Store secrets in environment variables
10. **CSRF Protection**: Add CSRF tokens to forms

## Customization

### Changing Admin Credentials
Edit the `init_db()` function in `app.py`:
```python
admin_password = generate_password_hash('your_new_password')
```

### Modifying Styles
Edit `/static/css/style.css` to customize colors, fonts, and layouts

### Adding Features
- Payment gateway integration
- QR code generation
- Transaction receipts
- Email notifications
- Two-factor authentication

## Troubleshooting

### Database Issues
If you encounter database errors:
```bash
rm securepay.db
python3 app.py  # Database will be recreated
```

### Port Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Template Not Found
Ensure all templates are in the `templates/` directory

## Future Enhancements

- [ ] Real SMS OTP integration
- [ ] QR code payment functionality
- [ ] Transaction receipt generation
- [ ] Email notifications
- [ ] Multi-factor authentication
- [ ] Payment gateway integration
- [ ] Mobile app (React Native/Flutter)
- [ ] Merchant payment QR codes
- [ ] Analytics and reporting
- [ ] Export transactions to PDF/Excel
- [ ] User profile management
- [ ] KYC verification
- [ ] Biometric authentication

## Development

### Running in Debug Mode
The application runs in debug mode by default for development:
```python
app.run(debug=True)
```

For production, set `debug=False`

### Testing
Create test users and merchants through the admin panel to test various workflows.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments in `app.py`
3. Ensure all dependencies are installed
4. Verify Python version compatibility

## License

This project is created for educational and demonstration purposes.

## Credits

Built with Flask, designed with modern UI principles, and inspired by real-world UPI payment systems.
