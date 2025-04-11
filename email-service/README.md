# Resume Analyzer Email Service

This is a Node.js microservice for sending emails to shortlisted candidates using Nodemailer.

## Setup

1. Install Node.js dependencies:

```
cd email-service
npm install
```

2. Configure email settings in `.env` file:

```
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
EMAIL_FROM=Resume Analyzer <your-email@gmail.com>

# Server Configuration
PORT=3000
```

> **Note:** For Gmail, you'll need to create an app password. Visit https://myaccount.google.com/apppasswords to generate one.

3. Start the email service:

```
node index.js
```




The service is automatically used by the Flask application when you:

1. Click the "Send Interview Invitation" button on a candidate card (for candidates with score >= 75%)
2. Click the "Send All Emails to Shortlisted Candidates" button at the bottom of the results page

## Troubleshooting

If emails are not being sent:

1. Check if the email service is running (`node index.js` in the email-service directory)
2. Verify your email credentials in the `.env` file
3. Make sure you're using an app password for Gmail
4. Check the console logs for any error messages
5. Test the email service directly by visiting http://localhost:3000/health
