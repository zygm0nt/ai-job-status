from rich.live import Live
from rich.table import Table
from rich import box

import sys
from time import sleep
import threading
import socket

import os

import pync

# from job_status_provider import DummyJobStatusProvider as CurrentProvider
# from job_status_provider import AIPlatformJobStatusProvider as CurrentProvider
from job_status_provider import GCloutAIPlatformJobStatusProvider as CurrentProvider

from job_db_file import JobDatabaseFile


TASKS = []
TASK_STATUSES = {}

CONSOLE = "https://console.cloud.google.com/ai-platform/jobs"
LOGS = "https://console.cloud.google.com/logs?resource=ml_job%2Fjob_id%2F"


def status_color(status):
    if status == "SUCCEEDED":
        return "[green]"
    elif status == "FAILED":
        return "[red]"
    else:
        return "[yellow]"


def status_hierarchy(status):
    if status == "SUCCEEDED":
        return 1
    elif status == "FAILED":
        return 1
    else:
        return 100


def sort_by_status(data):
    if len(data) == 0:
        return data
    data.sort(key=lambda x: (status_hierarchy(x[1].status), str(x[1].startTime)))
    return data


def generate_table() -> Table:
    remote_call_count = 0
    jobs_to_notify = set()
    for task in TASKS:
        if task.get_id() not in TASK_STATUSES or not TASK_STATUSES[task.get_id()][1].is_finished():
            _, status_changed, status = task.get_status()  # FIXME make this parallel call https://stackoverflow.com/questions/4992400/running-several-system-commands-in-parallel-in-python
            TASK_STATUSES[task.get_id()] = (task.get_id(), status)
            if status_changed:
                jobs_to_notify.add(task.get_id())
            remote_call_count += 1

    table = Table(show_lines=True,
                  title=":tent: Your log of jobs",
                  show_footer=True,
                  box=box.HEAVY_HEAD)
    table.add_column("ID")
    table.add_column("Value")
    table.add_column("Status")
    table.add_column("Link")
    table.add_column("MLUnits")
    table.add_column("Elapsed Time", footer=f"No of remote calls: {remote_call_count}",)

    for app_id, status in sort_by_status(list(TASK_STATUSES.values())):
        metrics = task.get_metrics()
        if app_id in jobs_to_notify:
            pync.Notifier.notify(f"{status.status} ✨ Status for '{app_id}' changed to '{status.status}")
        table.add_row(
            f"{app_id}",
            #f"{status.labels}",
            "",
            f"{status_color(status.status)}{status.status}",
            f':moai: {CONSOLE}/{app_id}\n:page_with_curl: {LOGS}{app_id}',
            str(status.consumedMLUnits),
            str(status.get_elapsed_time())
        )
    return table


def simpleServer():
    HOST = '127.0.0.1'
    PORT = 3000
    sock = socket.socket()
    sock.bind((HOST, PORT))

    job_db = JobDatabaseFile()
    for job_id in job_db.get_all():
        handle_user_input(job_id.strip(), notify=False)

    sock.listen(5)
    while True:
        conn, addr = sock.accept()
        msg = str(conn.recv(1024), 'utf8')
        conn.send(bytes('GOT: {0}'.format(msg), 'utf8'))
        handle_user_input(msg)
        job_db.update(msg)
        conn.close()


server_thread = threading.Thread(target=simpleServer)

CURRENT_PROJECT = os.environ.get('PROJECT_ID')


def handle_user_input(data, notify=True):
    TASKS.append(CurrentProvider(CURRENT_PROJECT, data))
    if notify:
        pync.Notifier.notify(f"Will keep an eye on '{data}'")


try:
    server_thread.start()
    with Live(generate_table(), refresh_per_second=4) as live:
        while True:
            sleep(1)
            live.update(generate_table())

except (KeyboardInterrupt, SystemExit):
    sys.exit()
