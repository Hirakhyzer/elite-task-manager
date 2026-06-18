from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from task_manager import Task, filter_tasks, project_progress, summarize_tasks, tasks_to_csv

BRAND_GOLD = "#f4af00"

st.set_page_config(page_title="Elite Task Manager", page_icon="⚡", layout="wide")

st.markdown(
    f"""
    <style>
    .main {{ background: linear-gradient(135deg, #000 0%, #111 55%, #241b00 100%); }}
    .hero {{ padding: 2rem; border-radius: 26px; background:#050505; border:1px solid {BRAND_GOLD}; color:#fff; }}
    .hero h1 {{ font-size: 3rem; margin-bottom:.4rem; }}
    .gold {{ color:{BRAND_GOLD}; }}
    .card {{ padding:1rem; border-radius:20px; background:#fff; color:#000; border:1px solid {BRAND_GOLD}; }}
    .value {{ font-size:2rem; font-weight:900; }}
    .timeline {{ padding:1rem; border-left:5px solid {BRAND_GOLD}; background:#fff; color:#111; border-radius:14px; margin-bottom:.65rem; }}
    .footer {{ text-align:center; color:#fff; padding:1.4rem; border-top:1px solid {BRAND_GOLD}; margin-top:2rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def default_rows():
    today = date.today()
    return [
        {"title": "Finalize landing page", "project": "Elite Website", "priority": "High", "status": "In Progress", "owner": "Hira", "due_date": today + timedelta(days=2), "notes": "Use gold brand color"},
        {"title": "Prepare client proposal", "project": "Client Work", "priority": "Critical", "status": "To Do", "owner": "Hira", "due_date": today + timedelta(days=1), "notes": "Add scope and timeline"},
        {"title": "Clean GitHub README files", "project": "Portfolio", "priority": "Medium", "status": "In Progress", "owner": "Hira", "due_date": today + timedelta(days=4), "notes": "Add SEO descriptions"},
        {"title": "Record app demo", "project": "Portfolio", "priority": "Medium", "status": "To Do", "owner": "Hira", "due_date": today + timedelta(days=6), "notes": "Short walkthrough"},
        {"title": "Review dashboard metrics", "project": "Elite Ops", "priority": "Low", "status": "Done", "owner": "Hira", "due_date": today - timedelta(days=1), "notes": "Completed"},
    ]


def rows_to_tasks(rows):
    if hasattr(rows, "to_dict"):
        rows = rows.to_dict("records")
    tasks = []
    for row in rows:
        if not str(row.get("title", "")).strip():
            continue
        tasks.append(
            Task(
                title=str(row.get("title", "")).strip(),
                project=str(row.get("project", "General")).strip() or "General",
                priority=str(row.get("priority", "Medium")),
                status=str(row.get("status", "To Do")),
                owner=str(row.get("owner", "Hira")).strip() or "Hira",
                due_date=row.get("due_date", date.today()),
                notes=str(row.get("notes", "")).strip(),
            )
        )
    return tasks


if "task_rows" not in st.session_state:
    st.session_state["task_rows"] = default_rows()

st.markdown(
    """
    <div class="hero">
        <h1><span class="gold">Elite</span> Task Manager</h1>
        <p>Black, white, and gold productivity dashboard for priorities, progress, and exportable reports.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("1. Manage tasks")
edited_rows = st.data_editor(
    st.session_state["task_rows"],
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "priority": st.column_config.SelectboxColumn("Priority", options=["Low", "Medium", "High", "Critical"]),
        "status": st.column_config.SelectboxColumn("Status", options=["To Do", "In Progress", "Done"]),
        "due_date": st.column_config.DateColumn("Due date"),
    },
)

tasks = rows_to_tasks(edited_rows)
projects = ["All"] + sorted({task.project for task in tasks})
statuses = ["All", "To Do", "In Progress", "Done"]
priorities = ["All", "Low", "Medium", "High", "Critical"]

col1, col2, col3 = st.columns(3)
with col1:
    selected_project = st.selectbox("Project", projects)
with col2:
    selected_status = st.selectbox("Status", statuses)
with col3:
    selected_priority = st.selectbox("Priority", priorities)

visible_tasks = filter_tasks(tasks, selected_project, selected_status, selected_priority)
report = summarize_tasks(visible_tasks)
progress = project_progress(visible_tasks)

st.markdown("## 2. Dashboard")
metric_cols = st.columns(4)
metrics = [
    ("Total", report.total_tasks),
    ("Open", report.open_tasks),
    ("Overdue", report.overdue_tasks),
    ("Completed", f"{report.completion_rate:.1f}%"),
]
for col, (label, value) in zip(metric_cols, metrics):
    with col:
        st.markdown(f"<div class='card'><div>{label}</div><div class='value'>{value}</div></div>", unsafe_allow_html=True)

for alert in report.alerts:
    st.warning(alert)

left, right = st.columns(2)
with left:
    st.subheader("Priority summary")
    st.dataframe([{"Priority": k, "Tasks": v} for k, v in report.priority_summary.items()], use_container_width=True, hide_index=True)
    if report.priority_summary:
        st.bar_chart(report.priority_summary)
with right:
    st.subheader("Project progress")
    st.dataframe([{"Project": k, "Completion": f"{v:.1f}%"} for k, v in progress.items()], use_container_width=True, hide_index=True)
    if progress:
        st.bar_chart(progress)

st.markdown("## 3. Upcoming tasks")
for task in report.upcoming_tasks:
    st.markdown(
        f"<div class='timeline'><b>{task.title}</b> · {task.priority} · {task.status}<br>{task.project} · Owner: {task.owner} · Due: {task.due_date.isoformat()} · {task.days_left} days left<br>{task.notes}</div>",
        unsafe_allow_html=True,
    )

st.markdown("## 4. Export")
exp1, exp2, exp3 = st.columns(3)
with exp1:
    st.download_button("Download CSV", data=tasks_to_csv(visible_tasks), file_name="elite_tasks.csv", mime="text/csv", use_container_width=True)
with exp2:
    st.download_button("Download JSON", data=report.to_json(), file_name="elite_task_report.json", mime="application/json", use_container_width=True)
with exp3:
    st.download_button("Download TXT", data=report.to_text(), file_name="elite_task_report.txt", mime="text/plain", use_container_width=True)

st.markdown(
    """
    <div class="footer">
        <strong style="color:#f4af00;">Made by Hira Khyzer</strong><br>
        Elite Era Development L.L.C
    </div>
    """,
    unsafe_allow_html=True,
)
