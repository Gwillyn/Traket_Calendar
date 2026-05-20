from tkinter import filedialog
from datetime import datetime, timezone
import database


def import_ics(tasktree, calendar, calendar_events):
    file_path = filedialog.askopenfilename(
        filetypes=[("ICS files", "*.ics"), ("All files", "*.*")]
    )
    if not file_path:
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]

    event_data = {}
    inside_event = False
    for line in lines:
        if line == "BEGIN:VEVENT":
            inside_event = True
            event_data = {}
        elif line == "END:VEVENT":
            inside_event = False
            title = event_data.get("SUMMARY", "Untitled")
            description = event_data.get("DESCRIPTION", "")
            dtstart = event_data.get("DTSTART")
            dtend = event_data.get("DTEND")

            if dtstart and dtend:
                # UTC parsing
                start_datetime = datetime.strptime(dtstart, "%Y%m%dT%H%M%SZ").replace(
                    tzinfo=timezone.utc
                )
                end_datetime = datetime.strptime(dtend, "%Y%m%dT%H%M%SZ").replace(
                    tzinfo=timezone.utc
                )

                # Make into local time only
                start_datetime = start_datetime.astimezone().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                end_datetime = end_datetime.astimezone().strftime("%Y-%m-%d %H:%M:%S")
                database.add_task(
                    title,
                    description,
                    start_datetime,
                    end_datetime,
                )

        elif inside_event:
            if ":" in line:
                key, value = line.split(":", 1)
                event_data[key] = value
    print("Import complete")

    import ui

    ui.refresh_tasks(tasktree)
    ui.refresh_calendar(calendar, calendar_events)
    ui.show_day_calendar(calendar, calendar_events)


def export_ics():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".ics",
        filetypes=[("ICS files", "*.ics"), ("All files", "*.*")],
        title="Save calendar as ICS",
    )

    if not file_path:
        return

    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Task Manager//EN"]

    tasks = database.get_tasks()

    for e in tasks:
        task_id, title, description, start_datetime, due_datetime, complete = e

        start_dt = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(due_datetime, "%Y-%m-%d %H:%M:%S")

        dtstart = start_dt.strftime("%Y%m%dT%H%M%S")
        dtend = end_dt.strftime("%Y%m%dT%H%M%S")

        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{task_id}",
                f"SUMMARY:{title}",
                f"DTSTART:{dtstart}",
                f"DTEND:{dtend}",
                f"DESCRIPTION:{description}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
