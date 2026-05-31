# Project Name

Assigmnet submission.

---

## Prerequisites

Ensure the following software is installed before setting up the project:

* Python 3.11+
* Git
* Virtual Environment support (`venv`)

Verify installation:

```bash
python --version
git --version
```

---

## Clone the Repository

```bash
git clone <repository-url>
cd <project-directory>
```

---

## Create and Activate Virtual Environment

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install poetry 
poetry install --no-root
```

---

## Configure Environment Variables

Create a `.env` file in the project root directory.

Example:

```env
APP_NAME = "finominal-web-api" or any name of your choice
```

---

## Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload
```

Application URLs:

| Service    | URL                         |
| ---------- | --------------------------- |
| API        | http://localhost:8000       |
| Swagger UI | http://localhost:8000/docs  |
| ReDoc      | http://localhost:8000/redoc |

##

---

## Project Structure

```text
project-root/
│
├── app/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   └── main.py
|
│
├── pyproject.toml
├── .env
└── README.md
```

---

## API Documentation

Once the application is running:

### Swagger UI

```text
http://localhost:8000/docs
```

### ReDoc

```text
http://localhost:8000/redoc
```

---

## Development Workflow

1. Pull latest changes from the target branch.
2. Create a feature branch.
3. Implement changes.
4. Create Pull Request.
5. Obtain code review approval.
6. Merge into target branch.

Example:

```bash
git checkout develop
git pull origin develop

git checkout -b feature/my-feature
```

---

## Troubleshooting

Check:

* Database server is running
* Credentials in `.env`
* Database exists
* Network connectivity

### Missing Dependencies

Recreate virtual environment:

```bash
rm -rf venv

python -m venv venv

source venv/bin/activate

poetry install --no-root
```

##

---

## Coding Standards

* Follow PEP 8 guidelines.
* Use type hints wherever possible.
* Write unit tests for new functionality.
* Keep business logic in service layer.
* Keep database access in repository layer.
* Use Alembic for all schema changes.

---

## Contributors

| Name       | Role           |
| ---------- | -------------- |
| Sudharshan | Sole Developer |
