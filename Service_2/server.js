// server.js
const express = require('express');
const mongoose = require('./configs/mongoose.js');
require('dotenv').config();
const cors = require('cors');

const notificationRoutes = require('./routes/notification');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
// Enable CORS
app.use(cors());
app.use(express.json());

// Routes
app.use('/api', notificationRoutes);

app.listen(PORT, () => {
  console.log(`Mail Notification Service running on port ${PORT}`);
});