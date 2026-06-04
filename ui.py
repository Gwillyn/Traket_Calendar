import database
import tkinter as tk
from tkinter import ttk
from datetime import date, datetime
import ics_manager as ics
from tkcalendar import Calendar


text_font = "JetBrainsMono Nerd Font"
dark_mode = False


def main_display():

    root = tk.Tk()
    root.title("Traket")
    root.geometry("900x800")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    style = ttk.Style()
    style.configure("TButton", font=(text_font, 12))
    style.configure("TNotebook.Tab", font=(text_font, 12, "bold"))

    # Main Frame
    mainframe = ttk.Frame(root)
    mainframe.grid(column=0, row=0, sticky=("nwes"))

    mainframe.columnconfigure(0, weight=1)
    mainframe.columnconfigure(1, weight=1)
    mainframe.columnconfigure(2, weight=1)
    mainframe.rowconfigure(1, weight=1)

    # Header Frame
    headerframe = ttk.Frame(mainframe)
    headerframe.grid(column=1, row=0, sticky="ew", pady=(80, 70))
    headerframe.columnconfigure(0, weight=1)

    ttk.Label(
        headerframe,
        text="Traket Calendar",
        font=(text_font, 30, "bold"),
        anchor="center",
    ).grid(column=0, row=0)

    # Task Area
    taskframe = ttk.Frame(mainframe)
    taskframe.grid(column=1, row=1, sticky="new")
    taskframe.columnconfigure(0, weight=1)
    taskframe.rowconfigure(0, weight=1)

    buttonframe = ttk.Frame(taskframe)
    buttonframe.grid(column=1, row=0, sticky="ne", padx=(0, 30), pady=(50, 0))

    settings_button = ttk.Button(
        buttonframe,
        text="Settings",
        command=lambda: settings_display(root, tasktree, calendar, calendar_events),
    )
    settings_button.grid(column=0, row=1, pady=30, ipadx=10)

    create_task_button = ttk.Button(
        buttonframe,
        text="Create Task",
        command=lambda: create_display(root, tasktree, calendar, calendar_events),
    )
    create_task_button.grid(column=0, row=0, ipadx=1)

    # Notebook for list and calendar view
    notebook = ttk.Notebook(taskframe)
    notebook.grid(column=0, row=0, sticky="nsew", padx=30)

    # List Area
    listframe = ttk.Frame(notebook, relief="ridge", borderwidth=20)
    listframe.columnconfigure(0, weight=1)
    listframe.rowconfigure(0, weight=0)

    notebook.add(listframe, text="List: ")

    eventsframe = ttk.Frame(listframe)
    eventsframe.grid(column=0, row=0, sticky="nsew")
    eventsframe.rowconfigure(0, weight=1)
    eventsframe.columnconfigure(0, weight=1)

    tasktree = ttk.Treeview(
        eventsframe,
        columns=("title", "due date", "description"),
        show="headings",
        height=19,
    )
    tasktree.heading("title", text="Title: ")
    tasktree.heading("due date", text="Due Date: ")
    tasktree.heading("description", text="Description: ")

    tasktree.column("title", width=60)
    tasktree.column("due date", width=120)
    tasktree.column("description", width=120)

    tasktree.grid(column=0, row=0, sticky="nsew", padx=20)

    refresh_tasks(tasktree)

    # Right-click menu
    task_menu = tk.Menu(root, tearoff=0)
    task_menu.add_command(
        label="Edit",
        command=lambda: edit_selected_task(
            root, tasktree, tasktree, calendar, calendar_events
        ),
    )
    task_menu.add_command(
        label="Delete",
        command=lambda: delete_selected_task(
            tasktree, tasktree, calendar, calendar_events
        ),
    )

    def show_task_menu(event):
        item = tasktree.identify_row(event.y)

        if item:
            tasktree.selection_set(item)
            task_menu.tk_popup(event.x_root, event.y_root)

    tasktree.bind("<Button-3>", show_task_menu)
    tasktree.bind("<Button-2>", show_task_menu)
    tasktree.bind(
        "<Delete>",
        lambda e: delete_selected_task(tasktree, tasktree, calendar, calendar_events),
    )
    tasktree.bind(
        "<Return>",
        lambda e: edit_selected_task(
            root, tasktree, tasktree, calendar, calendar_events
        ),
    )

    # Calendar Area
    calendarframe = ttk.Frame(notebook, relief="ridge", borderwidth=20)
    calendarframe.columnconfigure(0, weight=1)

    notebook.add(calendarframe, text="Calendar: ")

    calendar = Calendar(calendarframe, selectmode="day", date_pattern="mm/dd/yy")
    calendar.grid(column=0, row=0, sticky="nsew", padx=20, pady=20)

    calendar_events = ttk.Treeview(
        calendarframe, columns=("title", "time", "description"), show="headings"
    )
    calendar_events.heading("title", text="Title")
    calendar_events.heading("time", text="Time")

    # Hides the description column, it is only here for the right-click menu not to break with its indexing
    calendar_events.heading("description", text="Description")
    calendar_events.column("description", width=0, stretch=False)

    calendar_events.grid(column=0, row=1, sticky="ew", padx=20)
    calendar.bind(
        "<<CalendarSelected>>", lambda e: show_day_calendar(calendar, calendar_events)
    )

    refresh_calendar(calendar, calendar_events)

    # Right-click menu
    calendar_menu = tk.Menu(root, tearoff=0)
    calendar_menu.add_command(
        label="Edit",
        command=lambda: edit_selected_task(
            root, calendar_events, tasktree, calendar, calendar_events
        ),
    )
    calendar_menu.add_command(
        label="Delete",
        command=lambda: delete_selected_task(
            calendar_events, tasktree, calendar, calendar_events
        ),
    )

    def show_calendar_task_menu(event):
        item = calendar_events.identify_row(event.y)
        if item:
            calendar_events.selection_set(item)
            calendar_menu.tk_popup(event.x_root, event.y_root)

    calendar_events.bind("<Button-3>", show_calendar_task_menu)
    calendar_events.bind("<Button-2>", show_calendar_task_menu)
    calendar_events.bind(
        "<Delete>",
        lambda e: delete_selected_task(
            calendar_events, tasktree, calendar, calendar_events
        ),
    )
    calendar_events.bind(
        "<Return>",
        lambda e: edit_selected_task(
            root, calendar_events, tasktree, calendar, calendar_events
        ),
    )

    root.mainloop()


def settings_display(root, tasktree, calendar, calendar_events, width=600, height=400):
    settings_pop = popup_window(root, "Settings", width, height)

    ttk.Label(settings_pop, text="> SETTINGS", font=(text_font, 25, "bold")).grid(
        column=0, row=0, padx=(10, 0)
    )

    import_button = ttk.Button(
        settings_pop,
        text="Import ICS",
        command=lambda: ics.import_ics(tasktree, calendar, calendar_events),
    )
    import_button.grid(column=0, row=1, padx=20, pady=(10, 40))

    export_button = ttk.Button(
        settings_pop, text="Export ICS", command=lambda: ics.export_ics()
    )
    export_button.grid(column=0, row=2, padx=20)


def create_display(root, tasktree, calendar, calendar_events, width=600, height=600):
    create_pop = popup_window(root, "Create Task", width, height)

    ttk.Label(create_pop, text="> Create Task", font=(text_font, 25, "bold")).grid(
        column=0, row=0, pady=(0, 20), padx=(10, 0)
    )
    # Title entry
    ttk.Label(create_pop, text="Title: ", font=(text_font, 16)).grid(
        column=0, row=1, sticky="w", padx=(10, 0)
    )
    title_entry = ttk.Entry(create_pop, width=30)
    title_entry.grid(column=0, row=2)

    # Description Entry
    ttk.Label(create_pop, text="Description: ", font=(text_font, 16)).grid(
        column=0, row=3, sticky="w", pady=(40, 0), padx=(10, 0)
    )
    desc_entry = ttk.Entry(create_pop, width=30)
    desc_entry.grid(column=0, row=4)

    # Due date and time entry
    ttk.Label(create_pop, text="Time: ", font=(text_font, 16)).grid(
        column=1, row=1, sticky="w", padx=(10, 0)
    )

    hour = tk.StringVar(value="12")
    minute = tk.StringVar(value="00")
    ampm = tk.StringVar(value="AM")

    hour_box = ttk.Spinbox(create_pop, from_=1, to=12, textvariable=hour, width=10)
    minute_box = ttk.Spinbox(create_pop, from_=0, to=59, textvariable=minute, width=10)
    ampm_box = ttk.Combobox(
        create_pop,
        values=["AM", "PM"],
        textvariable=ampm,
        width=5,
        state="readonly",
        height=10,
    )

    hour_box.grid(column=1, row=2, sticky="w", padx=(25, 0))
    ttk.Label(create_pop, text=":", font=(text_font, 16)).grid(
        column=2, row=2, sticky="w"
    )
    minute_box.grid(column=3, row=2, sticky="w")
    ampm_box.grid(column=4, row=2, sticky="w")

    date_entry = Calendar(create_pop, selectmode="day", date_pattern="mm/dd/yy")
    date_entry.grid(column=1, row=4, padx=(20, 0), columnspan=3, rowspan=3)

    def submit_handler():
        hours = int(hour.get())
        minutes = int(minute.get())
        ampms = ampm.get()

        if ampms == "PM" and hours != 12:
            hours += 12
        elif ampms == "AM" and hours == 12:
            hours = 0

        full_time = datetime.strptime(f"{hours}:{minutes}", "%H:%M").time()
        stripped_date = datetime.strptime(date_entry.get_date(), "%m/%d/%y")

        database.add_task(
            title_entry.get(),
            desc_entry.get(),
            f"{datetime.now().date()} {datetime.now().time()}",
            datetime.combine(stripped_date.date(), full_time).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )
        refresh_tasks(tasktree)
        refresh_calendar(calendar, calendar_events)
        show_day_calendar(calendar, calendar_events)

        create_pop.destroy()

    # Submit
    submit = ttk.Button(create_pop, text="Submit", command=submit_handler)
    submit.grid(column=0, row=8)


def popup_window(root, title, width, height):
    name = tk.Toplevel(root)
    name.title(title)

    # This grabs the new window and opens it in the middle of the screen.
    # also, it lets any window managers know to keep the window floating
    name.transient(root)
    name.grab_set()
    name.wm_attributes(
        "-type", "utility"
    )  # lets WM know to float window since it is read as a utility
    screen_w = name.winfo_screenwidth()
    screen_h = name.winfo_screenheight()
    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)
    name.geometry(f"{width}x{height}+{x}+{y}")
    return name


def refresh_tasks(tasktree):
    for i in tasktree.get_children():
        tasktree.delete(i)

    tasks = database.get_tasks()

    for e in tasks:
        task_id, title, desc, start_date, due_date, complete = e

        # Display time and date in a readable format
        due = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
        event_time = due.strftime("%I:%M %p")
        event_date = due.strftime("%Y-%m-%d")

        if due.date() == date.today():
            date_set = event_time + "  " + "Today"
        else:
            date_set = event_time + "  " + event_date

        # Insert the event details into the tree
        tasktree.insert("", "end", iid=task_id, values=(title, date_set, desc))
    first_task_select(tasktree)


def refresh_calendar(calendar, calendar_events):
    calendar.calevent_remove("all")

    for i in calendar_events.get_children():
        calendar_events.delete(i)

    tasks = database.get_tasks()

    for e in tasks:
        task_id, title, desc, start_date, due_date, complete = e

        due = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")

        event_label = f"{due.strftime('%I:%M %p')} {title}"

        calendar.calevent_create(due.date(), event_label, "task")
    calendar.tag_config("task", background="green", foreground="black")


def show_day_calendar(calendar, calendar_events):
    for i in calendar_events.get_children():
        calendar_events.delete(i)

    selected_day = calendar.selection_get()
    tasks = database.get_tasks()

    for e in tasks:
        task_id, title, desc, start_date, due_date, complete = e
        due = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")

        if due.date() == selected_day:
            calendar_events.insert(
                "",
                "end",
                iid=task_id,
                values=(title, due.strftime("%I:%M %p"), desc),
            )


def delete_selected_task(selected_tree, tasktree, calendar, calendar_events):
    select = selected_tree.selection()

    if not select:
        return

    task_id = select[0]
    database.delete_task(task_id)

    refresh_tasks(tasktree)
    refresh_calendar(calendar, calendar_events)
    show_day_calendar(calendar, calendar_events)


def edit_selected_task(
    root, selected_tree, tasktree, calendar, calendar_events, width=600, height=400
):
    select = selected_tree.selection()

    if not select:
        return

    task_id = select[0]
    values = selected_tree.item(task_id, "values")

    old_title = values[0]
    old_description = values[2]

    edit_pop = popup_window(root, "Edit Task", width, height)

    ttk.Label(edit_pop, text="> Edit Task", font=(text_font, 25, "bold")).grid(
        column=0, row=0, pady=(0, 20), padx=(10, 0), sticky="nw"
    )

    ttk.Label(edit_pop, text="Title: ", font=(text_font, 16)).grid(
        column=0, row=1, sticky="w", padx=(10, 0)
    )

    title_entry = ttk.Entry(edit_pop, width=30)
    title_entry.insert(0, old_title)
    title_entry.grid(column=0, row=2, sticky="w", padx=(10, 0))

    ttk.Label(edit_pop, text="Description: ", font=(text_font, 16)).grid(
        column=0, row=3, sticky="w", pady=(40, 0), padx=(10, 0)
    )
    desc_entry = ttk.Entry(edit_pop, width=60)
    desc_entry.insert(0, old_description)
    desc_entry.grid(column=0, row=4, sticky="w", pady=(40, 0), padx=(10, 0))

    def submit_edit():
        database.update_task(
            task_id,
            title_entry.get(),
            desc_entry.get(),
        )

        refresh_tasks(tasktree)
        refresh_calendar(calendar, calendar_events)
        show_day_calendar(calendar, calendar_events)

        edit_pop.destroy()

    submit = ttk.Button(edit_pop, text="Save", command=submit_edit)
    submit.grid(column=0, row=8, pady=20)


# select the first task in the list automatically (mostly for keyboard navigation)
def first_task_select(tasktree):
    child = tasktree.get_children()

    if child:
        first = child[0]
        tasktree.selection_set(first)
        tasktree.focus(first)
        tasktree.focus_set()
