# QuickVisa

QuickVisa is a comprehensive visa application management system designed to automate and streamline the process of managing visa applications and scheduling appointments. The application monitors applicant credentials, automatically checks for available appointment slots, and manages rescheduling workflows.

## 📋 Project Overview

QuickVisa consists of two main components:

- **Frontend Client**: A modern React-based web application for managing applicants and configurations
- **Backend API**: A FastAPI-powered RESTful API that handles business logic, database operations, and automated scheduling tasks

The system integrates with Supabase for data persistence and uses Selenium for automated web scraping and credential validation.

## 🛠️ Tech Stack

### Frontend (`nextvisa-client`)

- **React 19.2** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **React Router DOM** - Client-side routing
- **TanStack Query (React Query)** - Server state management
- **Axios** - HTTP client
- **FontAwesome** - Icon library
- **React Toastify** - Toast notifications
- **Supabase Client** - Database client

### Backend (`nextvisa-api`)

- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Supabase** - PostgreSQL database and authentication
- **Pydantic** - Data validation
- **Selenium** - Web automation for credential testing
- **APScheduler** - Background job scheduling
- **Passlib** - Password hashing
- **Python-dotenv** - Environment variable management

## 📁 Project Structure

```
QuickVisa/
├── nextvisa-client/          # Frontend React application
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── nextvisa-api/             # Backend FastAPI application
│   ├── controllers/          # API route handlers
│   ├── services/            # Business logic
│   ├── models/              # Data models
│   ├── lib/                 # Core libraries (state machine, etc.)
│   ├── utils/               # Utility functions
│   ├── main.py              # Application entry point
│   └── requirements.txt
├── .github/                  # GitHub Actions workflows
└── README.md
```

## ⚙️ Prerequisites

Before running the project, ensure you have the following installed:

- **Node.js** (v18 or higher) and npm
- **Python** (v3.11 or higher)
- **Git**
- A **Supabase** account and project

## 🚀 Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Urias-Flores/QuickVisa.git
cd QuickVisa
```

### 2. Backend Setup

Navigate to the API directory and set up the Python environment:

```bash
cd nextvisa-api
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the `nextvisa-api` directory with your configuration:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
# Add other necessary environment variables
```

### 3. Frontend Setup

Navigate to the client directory:

```bash
cd ../nextvisa-client
```

Install dependencies:

```bash
npm install
```

Create a `.env` file in the `nextvisa-client` directory:

```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## 🏃 Running the Project

### Start the Backend API

From the `nextvisa-api` directory with the virtual environment activated:

```bash
python -m uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

- API Documentation (Swagger): `http://localhost:8000/docs`
- Alternative Documentation (ReDoc): `http://localhost:8000/redoc`

### Start the Frontend Client

From the `nextvisa-client` directory:

```bash
npm run dev
```

The client will be available at `http://localhost:5173`

## 🔑 Key Features

- **Applicant Management**: Create, read, update, and delete applicant information
- **Credential Testing**: Automated validation of applicant credentials using Selenium
- **Automatic Scheduling**: Background job that monitors and schedules visa appointments
- **Configuration Management**: Centralized settings for the application
- **Real-time Notifications**: Toast notifications for user feedback
- **State Machine**: Automated workflow management for appointment scheduling

## 📝 API Endpoints

- `GET /` - API health check
- `GET /status` - Detailed service status
- `/api/configuration` - Configuration management endpoints
- `/api/applicants` - Applicant CRUD operations
- `/api/re-schedules` - Rescheduling management

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Urias Flores

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error:**

- Ensure your Supabase credentials are correct in the `.env` file
- Check that your Supabase project is active

**CORS Issues:**

- Verify the frontend URL is included in the CORS settings in `main.py`
- Default allowed origins: `http://localhost:5173`, `http://localhost:3000`

**Selenium Errors:**

- Ensure you have the appropriate web driver installed (Chrome/Firefox)
- Check that your system PATH includes the driver location
