#!/bin/bash

# Start frontend script with correct API URL
cd /home/noor/alpha-learning-platform/frontend

# Set environment variables
export VITE_API_URL='http://localhost:5000'

# Start the frontend
npm run dev

