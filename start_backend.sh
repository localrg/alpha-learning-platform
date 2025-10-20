#!/bin/bash

# Start backend script
cd /home/noor/alpha-learning-platform/backend

# Set environment variables
export DATABASE_URL='sqlite:///./alphalearning.db'
export SECRET_KEY='dev-secret-key-change-in-production'
export JWT_SECRET_KEY='dev-jwt-secret-key-change-in-production'
export FLASK_ENV='development'
export PYTHONPATH='/home/noor/alpha-learning-platform/backend'

# Start the backend
python3 src/main.py

