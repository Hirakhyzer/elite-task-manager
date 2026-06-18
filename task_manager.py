"""Core logic for the Elite Task Manager app."""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path

PRIORITY_ORDER = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
STATUS_DONE = "Done"


@dataclass
class Task:
    title: str
    project: str
    priority: str
    status: str
    owner: str
    due_date: date
    notes: str = ""

    @property
    def days_left(self) -> int:
        return (self.due_date - date.today()).days

    def is_done(self) -> bool:
        return self.status == STATUS_DONE

    def is_overdue(self, today: date | None = None) -> bool:
        today = today or date.today()
        return self.due_date < today and not self.is_done()


@dataclass
class TaskReport:
    total_tasks: int
    done_tasks: int
    open_tasks: int
    overdue_tasks: int
    completion_rate: float
    priority_summary: dict[str, int]
    status_summary: dict[str, int]
    project_summary: dict[str, int]
    alerts: list[str]
    upcoming_tasks: list[Task]

    def to_dict(self) -> dict:
        return {
            "total_tasks": self.total_tasks,
            "done_tasks": self.done_tasks,
            "open_tasks": self.open_tasks,
            "overdue_tasks": self.overdue_tasks,
            "completion_rate": self.completion_rate,
            "priority_summary": self.priority_summary,
            "status_summary": self.status_summary,
            "project_summary": self.project_summary,
            "alerts": self.alerts,
            "upcoming_tasks": [
                {**asdict(task), "due_date": task.due_date.isoformat(), "days_left": task.days_left}
                for task in self.upcoming_tasks
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_text(self) -> str:
        lines = [
            "Elite Task Manager Report",
            "==========================",
            f"Total tasks: {self.total_tasks}",
            f"Done tasks: {self.done_tasks}",
            f"Open tasks: {self.open_tasks}",
            f"Overdue tasks: {self.overdue_tasks}",
            f"Completion rate: {self.completion_rate:.1f}%",
            "",
            "Priority summary:",
        ]
        lines.extend(f"- {name}: {count}" for name, count in self.priority_summary.items())
        lines.append("")
        lines.append("Project summary:")
        lines.extend(f"- {name}: {count}" for name, count in self.project_summary.items())
        if self.alerts:
            lines.append("")
            lines.append("Alerts:")
            lines.extend(f"- {alert}" for alert in self.alerts)
        return "\n".join(lines) + "\n"


def parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def load_tasks_from_csv(path: str | Path) -> list[Task]:
    with Path(path).open(newline="", encoding="utf-8") as file:
        rows = csv.DictReader(file)
        return [
            Task(
                title=row["title"].strip(),
                project=row["project"].strip(),
                priority=row["priority"].strip(),
                status=row["status"].strip(),
                owner=row["owner"].strip(),
                due_date=parse_date(row["due_date"]),
                notes=row.get("notes", "").strip(),
            )
            for row in rows
        ]


def completion_rate(tasks: list[Task]) -> float:
    if not tasks:
        return 0.0
    done_count = sum(task.is_done() for task in tasks)
    return round(done_count / len(tasks) * 100, 1)


def summarize_tasks(tasks: list[Task], today: date | None = None) -> TaskReport:
    today = today or date.today()
    total = len(tasks)
    done = sum(task.is_done() for task in tasks)
    overdue = sum(task.is_overdue(today) for task in tasks)
    open_count = total - done

    priority_summary = dict(Counter(task.priority for task in tasks))
    status_summary = dict(Counter(task.status for task in tasks))
    project_summary = dict(Counter(task.project for task in tasks))

    alerts = []
    if overdue:
        alerts.append(f"{overdue} task(s) are overdue and still open.")
    critical_open = [task for task in tasks if task.priority == "Critical" and not task.is_done()]
    if critical_open:
        alerts.append(f"{len(critical_open)} critical task(s) need attention.")
    if not tasks:
        alerts.append("Add tasks to generate dashboard insights.")

    upcoming = sorted(
        [task for task in tasks if not task.is_done()],
        key=lambda task: (task.due_date, -PRIORITY_ORDER.get(task.priority, 0)),
    )[:8]

    return TaskReport(
        total_tasks=total,
        done_tasks=done,
        open_tasks=open_count,
        overdue_tasks=overdue,
        completion_rate=completion_rate(tasks),
        priority_summary=priority_summary,
        status_summary=status_summary,
        project_summary=project_summary,
        alerts=alerts,
        upcoming_tasks=upcoming,
    )


def filter_tasks(tasks: list[Task], project: str = "All", status: str = "All", priority: str = "All") -> list[Task]:
    filtered = tasks
    if project != "All":
        filtered = [task for task in filtered if task.project == project]
    if status != "All":
        filtered = [task for task in filtered if task.status == status]
    if priority != "All":
        filtered = [task for task in filtered if task.priority == priority]
    return filtered


def tasks_to_csv(tasks: list[Task]) -> str:
    lines = ["title,project,priority,status,owner,due_date,notes"]
    for task in tasks:
        safe_notes = task.notes.replace(",", " ")
        lines.append(
            f"{task.title},{task.project},{task.priority},{task.status},{task.owner},{task.due_date.isoformat()},{safe_notes}"
        )
    return "\n".join(lines) + "\n"


def project_progress(tasks: list[Task]) -> dict[str, float]:
    grouped: dict[str, list[Task]] = defaultdict(list)
    for task in tasks:
        grouped[task.project].append(task)
    return {project: completion_rate(items) for project, items in grouped.items()}
