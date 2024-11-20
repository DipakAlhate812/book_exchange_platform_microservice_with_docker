// models/Notification.js
const mongoose = require('mongoose');

const notificationSchema = new mongoose.Schema({
  email: { type: String, required: true },
  actionType: { type: String, required: true },
  message: { type: String, required: true },
  timestamp: { type: Date, default: Date.now }
});

// Create the Notification model
const Notification = mongoose.model('Notification', notificationSchema);

// Export the Notification model
module.exports = Notification;