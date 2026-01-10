# Email Configuration Guide

## Overview

The EHR system includes email functionality for account confirmation and password reset. When a new doctor registers, the system sends a confirmation email that must be clicked before the account can be used. The system also sends password reset emails when doctors request to reset their forgotten passwords.

The email system uses Flask-Mail and SMTP to send emails. Email templates are stored in the `templates/email/` directory and include HTML formatting for a professional appearance.

## Email Functionality

The system sends emails in two scenarios:

1. **Registration Confirmation**: When a new doctor registers, an email is sent with a confirmation link. The link contains a secure token that expires after 24 hours. Doctors must click this link to confirm their email address before they can log in.

2. **Password Reset**: When a doctor uses the "Forgot Password" feature, an email is sent with a password reset link. This link also contains a secure token that expires after 24 hours.

## Email Configuration Setup

### Step 1: Configure Environment Variables

The email configuration is stored in the `.env` file. After creating your `.env` file from `.env.example`, you need to set the following email-related variables:

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

Replace the placeholder values with your actual email credentials. The `MAIL_SERVER`, `MAIL_PORT`, and `MAIL_USE_TLS` values depend on your email provider.

### Step 2: Gmail Setup

If you are using Gmail, you need to create an app-specific password because Gmail requires two-factor authentication for SMTP access:

1. Enable 2-Factor Authentication on your Gmail account if it is not already enabled.

2. Go to your Google Account Settings, then navigate to Security → 2-Step Verification.

3. Scroll down to "App passwords" and click on it.

4. Generate a new app password:
   - Select "Mail" as the app type
   - Select "Other" as the device type
   - Enter a name like "EHR System"
   - Click "Generate"

5. Copy the 16-digit password that is generated.

6. Use this 16-digit password as the value for `MAIL_PASSWORD` in your `.env` file. **Do not use your regular Gmail password.**

### Step 3: Alternative Email Providers

If you are using a different email provider, you need to adjust the SMTP settings accordingly.

**For Outlook/Hotmail:**
```
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
```

**For Yahoo:**
```
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=True
```

For other email providers, consult their documentation for SMTP server settings. Most providers use port 587 with TLS enabled, but some may use different ports or require SSL instead of TLS.

## Email Templates

The system includes HTML email templates located in `templates/email/`:

- `email_confirmation.html`: Template for registration confirmation emails
- `password_reset_template.html`: Template for password reset emails

These templates include the doctor's name, a clear message explaining the purpose of the email, and a button or link to complete the action. The confirmation and reset links include secure tokens that expire after 24 hours for security.

## How Email Works in the System

When a doctor registers:

1. The registration form is submitted with the doctor's information.
2. The system creates a new doctor record in the database with `email_confirmed` set to `False`.
3. A secure token is generated using the doctor's ID and a purpose identifier ("confirm").
4. An email is sent using Flask-Mail with a link containing this token.
5. When the doctor clicks the link, the system verifies the token and sets `email_confirmed` to `True`.
6. The doctor can now log in.

The password reset process works similarly, but uses a "reset_password" purpose identifier and allows the doctor to set a new password.

## Security Features

The email system includes several security measures:

- **Token-based verification**: Confirmation and reset links contain secure tokens generated using the `itsdangerous` library. These tokens are signed and include expiration times.

- **Token expiration**: Tokens expire after 24 hours (86400 seconds) as defined in the configuration. This prevents old links from being used indefinitely.

- **Email confirmation required**: Doctors cannot log in until they confirm their email address. This prevents unauthorized account creation.

- **SMTP TLS encryption**: Email credentials and content are transmitted securely using TLS encryption when connecting to the SMTP server.

- **Password hashing**: While not directly related to email, the system uses password hashing for stored passwords, which works together with the email system to provide secure authentication.

## Troubleshooting

If emails are not being sent or received, check the following:

1. **Authentication errors**: If you see "Authentication failed" errors, verify that:
   - For Gmail, you are using an app-specific password, not your regular password
   - The `MAIL_USERNAME` and `MAIL_PASSWORD` in your `.env` file are correct
   - Two-factor authentication is enabled if using Gmail

2. **Connection errors**: If you see "SMTP connection failed" errors, check:
   - Your internet connection
   - The `MAIL_SERVER` address is correct for your email provider
   - The `MAIL_PORT` is correct (usually 587 for TLS)
   - Firewall settings are not blocking the connection

3. **Emails not received**: If emails are sent but not received:
   - Check the spam or junk folder
   - Verify the email address in the database is correct
   - Check that the email provider is not blocking the messages
   - Verify the `MAIL_DEFAULT_SENDER` address is valid

4. **Invalid token errors**: If confirmation or reset links show "Invalid or expired link":
   - Tokens expire after 24 hours, so old links will not work
   - Make sure you are clicking the most recent email link
   - Verify the token was not corrupted in the email

5. **Email sending fails silently**: The system includes error handling that catches exceptions during email sending. If an email fails to send, the system will display a message to the user, but the registration or password reset request may still be processed. Check the console output for detailed error messages.

## Testing Email Configuration

To test if email configuration is working:

1. Make sure all email variables are set correctly in your `.env` file.

2. Start the Flask application.

3. Try registering a new doctor account using a valid email address you can access.

4. Check your email inbox (and spam folder) for the confirmation email.

5. Click the confirmation link to verify it works correctly.

6. Try the "Forgot Password" feature to test password reset emails.

If emails are not being sent, check the Flask console output for error messages. The system prints error messages when email sending fails, which can help identify configuration issues.


**The email functionality is implemented and ready to use once you configure the email settings in your `.env` file.**