#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from modelserve.views import worker_info, set_is_controller, initialize_all
import argparse


def runserver_with_args():
    if "--controller" in sys.argv:
        run_controller_with_args()
    else:
        run_worker_with_args()


def run_controller_with_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--controller", action="store_true")
    parser.add_argument("--port", type=str)
    args = parser.parse_args()
    run_controller(args.port)


def run_worker_with_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--port", type=str)
    parser.add_argument("--name", type=str)
    parser.add_argument("--device", type=str)
    parser.add_argument("--controller-addr", type=str)
    parser.add_argument("--worker-addr", type=str)

    args = parser.parse_args()
    run_worker(
        args.port, args.name, args.device, args.controller_addr, args.worker_addr
    )


def run_controller(port: int):
    run(True, port, None, None, None, None)


def run_worker(port: int, name, device, controller_addr, worker_addr):
    run(False, port, name, device, controller_addr, worker_addr)


def run(_is_controller, port: int, name, device, controller_addr, worker_addr):
    global worker_info
    set_is_controller(_is_controller)
    if not _is_controller:
        worker_info.port = port
        worker_info.name = name
        worker_info.device = device
        worker_info.controller_addr = controller_addr
        worker_info.worker_addr = worker_addr
    initialize_all()

    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "modelserve.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(["run.py", "runserver", f"0.0.0.0:{port}", "--noreload"])
