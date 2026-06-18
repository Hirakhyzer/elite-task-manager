# Elite Task Manager

A branded Streamlit productivity dashboard for managing tasks, priorities, status, deadlines, progress, and exportable reports.

Built with the Elite Era Development L.L.C visual style: black, white, and `#f4af00` gold.

## Features

- Beautiful black, white, and gold Streamlit UI
- Editable task table
- Priority levels: Low, Medium, High, Critical
- Status tracking: To Do, In Progress, Done
- Deadline countdown and overdue warnings
- Project/category filtering
- Progress dashboard cards
- Priority and status summaries
- Recent task timeline
- Downloadable CSV, JSON, and TXT reports
- Built-in sample tasks
- Core task logic separated from UI
- Unit tests and GitHub Actions workflow

## Tech Stack

- Python
- Streamlit
- Standard-library task calculations
- Pytest

## Project Structure

```text
elite-task-manager/
├── app.py
├── task_manager.py
├── README.md
├── requirements.txt
├── pyproject.toml
├── .gitignore
├── sample_data/
│   └── sample_tasks.csv
├── tests/
│   └── test_task_manager.py
└── .github/
    └── workflows/
        └── python-tests.yml
```

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Run Tests

```bash
pytest
```

## How It Works

Each task has a title, project, priority, status, owner, deadline, and notes. The app calculates completion rate, overdue tasks, upcoming tasks, priority summaries, project summaries, and exportable reports.

---

## Author

Made by **Hira Khyzer**

Developed as part of the **Elite Era Development L.L.C** project portfolio.

Brand color: `#f4af00`
