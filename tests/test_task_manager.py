from datetime import date, timedelta

from task_manager import Task, completion_rate, filter_tasks, project_progress, summarize_tasks, tasks_to_csv


def sample_tasks():
    today = date(2026, 6, 18)
    return [
        Task("Build UI", "Website", "High", "In Progress", "Hira", today + timedelta(days=2), "Brand colors"),
        Task("Write README", "Portfolio", "Medium", "Done", "Hira", today - timedelta(days=1), "Complete"),
        Task("Client proposal", "Client Work", "Critical", "To Do", "Hira", today - timedelta(days=1), "Needs review"),
    ]


def test_completion_rate():
    assert completion_rate(sample_tasks()) == 33.3


def test_summarize_tasks_counts_overdue():
    today = date(2026, 6, 18)
    report = summarize_tasks(sample_tasks(), today=today)
    assert report.total_tasks == 3
    assert report.done_tasks == 1
    assert report.open_tasks == 2
    assert report.overdue_tasks == 1
    assert report.priority_summary["Critical"] == 1


def test_filter_tasks_by_project():
    filtered = filter_tasks(sample_tasks(), project="Website")
    assert len(filtered) == 1
    assert filtered[0].title == "Build UI"


def test_project_progress():
    progress = project_progress(sample_tasks())
    assert progress["Portfolio"] == 100.0
    assert progress["Website"] == 0.0


def test_tasks_to_csv_contains_header():
    csv_text = tasks_to_csv(sample_tasks())
    assert "title,project,priority,status,owner,due_date,notes" in csv_text
    assert "Build UI" in csv_text
