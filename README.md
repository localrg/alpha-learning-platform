# Alpha Learning Platform

A comprehensive, AI-powered mastery-based learning platform inspired by Alpha School's methodology. Designed to help students master mathematics through personalized, adaptive learning paths with 90% mastery requirements.

## Project Overview

The Alpha Learning Platform implements the proven Alpha School approach:
- **90% mastery requirement** before advancing (no knowledge gaps)
- **AI-powered personalized tutoring** (hints, feedback, explanations)
- **Gamification and motivation** (streaks, badges, time back rewards)
- **Parent dashboard** for monitoring and insights
- **Adaptive learning paths** based on assessment results

## Project Structure

```
alpha-learning-platform/
├── frontend/          # React + Vite frontend application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts (Auth, etc.)
│   │   ├── services/      # API services
│   │   ├── App.jsx        # Main app component
│   │   └── main.jsx       # Entry point
│   ├── public/            # Static assets
│   └── package.json       # Frontend dependencies
│
├── backend/           # Flask backend API
│   ├── src/
│   │   ├── models/        # Database models
│   │   ├── routes/        # API routes/blueprints
│   │   ├── services/      # Business logic (AI tutor, problem generator)
│   │   ├── database/      # Database files
│   │   └── main.py        # Flask app entry point
│   ├── venv/              # Python virtual environment
│   └── requirements.txt   # Python dependencies
│
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Technology Stack

### Frontend
- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **Axios** - HTTP client
- **React Router** - Routing
- **Framer Motion** - Animations

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - Authentication
- **OpenAI API** - AI tutoring features
- **SQLite** - Database (development)

## Setup Instructions

### Prerequisites
- Node.js 18+ and pnpm
- Python 3.11+
- Git

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies (already done during setup):
```bash
pnpm install
```

3. Start development server:
```bash
pnpm run dev
```

The frontend will be available at **http://localhost:5173**

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Activate virtual environment:
```bash
source venv/bin/activate
```

3. Install dependencies (if needed):
```bash
pip install -r requirements.txt
```

4. Start Flask server:
```bash
python src/main.py
```

The backend will be available at **http://localhost:5000**

### Running Both Servers

Open two terminal windows:

**Terminal 1 (Frontend):**
```bash
cd /home/ubuntu/alpha-learning-platform/frontend
pnpm run dev
```

**Terminal 2 (Backend):**
```bash
cd /home/ubuntu/alpha-learning-platform/backend
source venv/bin/activate
python src/main.py
```

## Development Workflow

1. **Make changes** to frontend or backend code
2. **Frontend auto-reloads** on file save (Vite HMR)
3. **Backend requires restart** after changes (Ctrl+C, then restart)
4. **Test in browser** at http://localhost:5173
5. **Commit changes** regularly with Git

## Git Workflow

```bash
# Check status
git status

# Add files
git add .

# Commit with message
git commit -m "Description of changes"

# View history
git log --oneline
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Student Profile
- `GET /api/student/profile` - Get student profile
- `POST /api/student/profile` - Create student profile
- `PUT /api/student/profile` - Update student profile

### Assessment
- `GET /api/assessment/diagnostic` - Get diagnostic assessment
- `POST /api/assessment/submit` - Submit assessment answers

### Learning
- `GET /api/student/learning-path` - Get personalized learning path
- `GET /api/skills/:id/practice` - Get practice problems for skill
- `POST /api/skills/:id/submit-answer` - Submit answer for problem
- `GET /api/skills/:id/hint` - Get AI-generated hint

## Environment Variables

Create `.env` files in both frontend and backend directories:

### Backend `.env`
```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
OPENAI_API_KEY=your-openai-api-key
DATABASE_URL=sqlite:///src/database/app.db
```

### Frontend `.env`
```
VITE_API_URL=http://localhost:5000
```

## Testing

### Frontend
```bash
cd frontend
pnpm run test
```

### Backend
```bash
cd backend
source venv/bin/activate
pytest
```

## Building for Production

### Frontend
```bash
cd frontend
pnpm run build
```
Output will be in `frontend/dist/`

### Backend
The Flask app is production-ready. For deployment:
1. Set environment variables
2. Use production WSGI server (gunicorn)
3. Configure database (PostgreSQL recommended)

## Troubleshooting

### Frontend won't start
- Check Node.js version: `node --version` (should be 18+)
- Delete `node_modules` and reinstall: `rm -rf node_modules && pnpm install`
- Check port 5173 is not in use

### Backend won't start
- Check Python version: `python --version` (should be 3.11+)
- Ensure virtual environment is activated
- Check port 5000 is not in use
- Verify all dependencies installed: `pip install -r requirements.txt`

### Database errors
- Delete database file: `rm backend/src/database/app.db`
- Run migrations: `flask db upgrade`

## Project Status

**Current Phase:** Step 1.1 - Environment Setup ✅

**Completed:**
- [x] Project structure created
- [x] Frontend initialized (React + Vite)
- [x] Backend initialized (Flask)
- [x] Git repository set up
- [x] README documentation

**Next Steps:**
- [ ] Database setup (SQLAlchemy models)
- [ ] Authentication system
- [ ] Student profile management
- [ ] Assessment system
- [ ] Learning session implementation

## Resources

- [Alpha School Methodology](https://alpha.school)
- [React Documentation](https://react.dev)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Tailwind CSS](https://tailwindcss.com)
- [OpenAI API](https://platform.openai.com/docs)

## License

Proprietary - Alpha Learning Platform

## Contact

For questions or issues, please refer to the project documentation.

---

**Built with ❤️ to help students master mathematics through personalized, AI-powered learning.**

