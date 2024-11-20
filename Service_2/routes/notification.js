// routes/notifications.js
const express = require('express');
const router = express.Router();
const Notification = require('../models/Notification');
const { sendMail } = require('../mailer');
const mongoose = require('mongoose');
// POST /notify - Send a notification email and log it to the database
router.post('/notify', async (req, res) => {
  const { actionType, email, details } = req.body;
  console.log(req.body);

  if (!actionType || !email) {
    return res.status(400).json({ error: "Action type and email are required." });
  }
 
  // Create the email message content
  const subject = `Notification: ${actionType}`;
  const message = `An action has been performed: ${actionType}.\nDetails: ${JSON.stringify(details)}`;

  try {
    // Send email
    await sendMail(email, subject, message);

    // Save notification history
    if (mongoose.connection.readyState === 1) {
      const notification = new Notification({
        email,
        actionType,
        message
      });
      await notification.save();
    } else {
      console.error('Database connection not established.', error.details);
      throw new Error('Database connection not established.');
    }
    
    res.status(200).json({ message: "Email notification sent and logged successfully." });
  } catch (error) {
    console.error("Error sending notification:", error);
    res.status(500).json({ error: "Failed to send and log notification.", details:error.message });
  }
});




module.exports = router;