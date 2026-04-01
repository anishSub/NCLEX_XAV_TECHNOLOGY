# NCLEX XAV Technology

NCLEX XAV Technology is a Django-based NCLEX-RN preparation platform built around adaptive testing, topic-based practice, clinical case scenarios, study planning, subscriptions, and gamified learning.

It combines a traditional web app with a question engine that supports modern NCLEX item types, performance tracking, and a browser-based study game.

## Overview

This repository contains the main web application for an NCLEX preparation product focused on:

- adaptive CAT-style mock exams
- topic-based question practice
- next-generation NCLEX item types
- clinical judgment scenarios with exhibits
- study planning and task tracking
- subscriptions and premium access
- gamification with streaks, points, badges, and leaderboard
- a browser-based RPG study game
- an admin panel for managing questions, scenarios, users, and exams

## Main Features

### 1. Adaptive NCLEX Exam Simulator

The app includes a computerized adaptive testing flow that:

- starts a new exam session for an authenticated user
- selects questions based on current ability estimate
- updates theta and standard error as answers are submitted
- applies pass/fail stopping logic
- tracks performance history across the exam
- supports long-form exam timing up to 5 hours

### 2. Practice by Category

Users can practice questions outside the CAT flow by selecting NCLEX categories. The project includes a category seeding command for the standard NCLEX-RN areas:

- Management of Care
- Safety and Infection Control
- Health Promotion and Maintenance
- Psychosocial Integrity
- Basic Care and Comfort
- Pharmacological and Parenteral Therapies
- Reduction of Risk Potential
- Physiological Adaptation

### 3. Next-Generation NCLEX Question Types

The question system is built to support multiple NCLEX item formats, including:

- Multiple Choice
- Select All That Apply
- Drag & Drop Rationale
- Matrix Multiple Response
- Dropdown Cloze Rationale
- Hot Spot
- Highlight Text

Questions are stored with flexible JSON-based option payloads, which makes the platform more adaptable for modern NCLEX content formats.

### 4. Clinical Scenario Practice

The scenarios module supports unfolding case studies with structured exhibits such as:

- patient history
- vital signs
- labs
- nurse's notes

Scenario questions can also track clinical judgment functions such as recognizing cues, analyzing cues, prioritizing hypotheses, generating solutions, taking actions, and evaluating outcomes.

### 5. Analytics and Reporting

The exam results flow includes analytics such as:

- theta progression across a session
- confidence interval bounds
- category breakdowns
- strongest and weakest areas
- time-per-question insights
- platform comparison metrics
- recommendation messages

The UI also advertises downloadable PDF reports for performance review.

### 6. Study Planner

The study planner module gives users a planning dashboard with:

- target exam date setup
- daily study-hour goals
- task scheduling
- task status management
- calendar views
- study streak tracking
- recommendation endpoints based on weak areas

### 7. Gamification

The platform includes a gamification layer with:

- user points
- levels
- login/activity streaks
- earned badges
- leaderboard ranking
- daily activity tracking

### 8. Subscription Flow

The subscriptions module supports:

- a free tier
- premium subscription activation
- subscription dashboard
- transaction records
- feature access tracking

The current checkout flow uses a test/manual activation path in the backend, while the data model is prepared for gateways such as eSewa, Khalti, Stripe, and manual transactions.

### 9. Browser-Based Adventure Game

The web app also includes a game mode where users answer NCLEX questions to battle enemies in an RPG-style interface.

Game highlights:

- browser-based access
- question-backed combat
- category-based gameplay
- score and streak-oriented study loop

## Tech Stack

- Backend: Django 6
- API utilities: Django REST Framework
- Database: PostgreSQL
- Authentication: Django auth + django-allauth
- Admin UI: Jazzmin
- Media/Image handling: Pillow
- Frontend delivery: Django templates, static CSS, static JavaScript
- Containerization: Docker and Docker Compose

## Project Structure

```text
.
├── nclex_core/          # Django project settings and root URLs
├── users/               # Authentication, profile, registration, password reset
├── questions/           # Question models, admin, question-type support
├── categories/          # NCLEX category data
├── scenarios/           # Clinical case study models
├── exam_sessions/       # Adaptive exam flow, practice flow, results, APIs
├── study_planner/       # Study plans, tasks, planner dashboard, recommendations
├── subscriptions/       # Pricing, checkout, access tracking
├── gamification/        # Points, badges, streaks, leaderboard
├── game/                # Browser-based NCLEX adventure game
├── pages/               # Landing page and simple content routes
├── static/              # Shared CSS, JS, theme assets
├── media/               # Uploaded media such as hotspot images
├── Design/              # Separate React + Vite design/prototype workspace
└── NCLEX/               # Separate pygame-based study/game prototype
```

## Main Routes

Some important routes exposed by the application:

| Route | Purpose |
| --- | --- |
| `/` | Landing page |
| `/auth/register/` | User registration |
| `/auth/login/` | User login |
| `/exam/start/` | Start adaptive exam |
| `/exam/practice/categories/` | Practice by category |
| `/exam/scenario/` | Scenario practice |
| `/planner/` | Study planner dashboard |
| `/subscriptions/pricing/` | Pricing page |
| `/subscriptions/dashboard/` | Subscription dashboard |
| `/gamification/leaderboard/` | Leaderboard |
| `/game/` | Adventure game entry page |
| `/admin/` | Admin panel |

## Authentication

The application uses a custom user model and supports:

- email-based registration and login
- password reset flows
- role-aware login redirect behavior
- social login integration hooks for Google and Facebook through django-allauth

To enable social login in a real deployment, corresponding provider credentials must be added to environment/configuration.

## Local Development

### Prerequisites

- Python 3.12+ recommended
- PostgreSQL
- pip / virtual environment tools

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd NCLEX_XAV_TECHNOLOGY
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create environment file

```bash
cp .env.example .env
```

### 5. Configure PostgreSQL

By default, the project is set up around these database values:

- database name: `nclex_db`
- username: `nclex_user`
- password: `nclex_password`
- host: `127.0.0.1` for local runs
- port: `5433` for local runs on macOS in the current settings

Create a matching PostgreSQL database locally, or adjust the settings/environment to fit your local setup.

### 6. Apply migrations

```bash
python manage.py migrate
```

### 7. Seed base data

```bash
python manage.py populate_categories
python manage.py populate_question_types
```

Optional demo content:

```bash
python manage.py create_demo_questions
```

### 8. Create an admin user

```bash
python manage.py createsuperuser
```

### 9. Run the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Docker Setup

The repository includes a `Dockerfile` and `docker-compose.yml` for running the app with PostgreSQL.

### Start the stack

```bash
cp .env.example .env
docker compose up --build
```

### Apply migrations inside the container

```bash
docker compose exec web python manage.py migrate
```

### Seed core data

```bash
docker compose exec web python manage.py populate_categories
docker compose exec web python manage.py populate_question_types
```

The app is exposed on:

- `http://localhost:8000`

The PostgreSQL service is mapped to host port:

- `5433`

## Content Management

Most operational content is managed through Django admin, including:

- questions
- question types
- categories
- scenarios
- exam sessions
- users
- subscription records
- gamification data

The admin panel uses Jazzmin for a more polished management UI.

## Extra Workspaces in This Repository

This repository also contains two side workspaces that are separate from the main Django web application:

### `Design/`

A React + TypeScript + Vite workspace with page prototypes and UI explorations for the product experience.

### `NCLEX/`

A standalone pygame-based study/game prototype with its own assets and dependency file.

These folders are useful for design exploration and alternate product experiments, but the main web app lives at the repository root.

## Current Notes

- The primary product is the Django web app at the repository root.
- The subscription backend currently includes a test/manual activation flow.
- Social login requires real provider credentials before production use.
- Demo seeding commands are available for categories, question types, and sample questions.

## Why This Project Stands Out

This project is more than a simple quiz application. It combines:

- CAT-style testing logic
- NGN item-type support
- scenario-based clinical reasoning
- study planning
- premium product structure
- gamified retention loops

That makes it a strong foundation for a full NCLEX preparation platform rather than just a question bank.
