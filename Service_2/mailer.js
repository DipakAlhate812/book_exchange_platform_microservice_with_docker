// mailer.js
const nodemailer = require('nodemailer');
require('dotenv').config();

const transporter = nodemailer.createTransport({
  
  host: process.env.SMTP_HOST,
  port: process.env.SMTP_PORT,
  secure: false, // use TLS
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS
  }
});

async function sendMail(to, subject, text) {
  const mailOptions = {
    from: process.env.FROM_EMAIL,
    to,
    subject,
    text
  };

  return transporter.sendMail(mailOptions);
}

module.exports = { sendMail };