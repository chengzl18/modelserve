from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from threading import Lock
import os
import requests
from typing import List
import json
from apscheduler.schedulers.background import BackgroundScheduler
import time

scheduler = BackgroundScheduler()
scheduler.start()

is_controller = True
registered_apis = {}


def api(name):
    global registered_apis

    def decorator(api_class):
        registered_apis[name] = api_class
        return api_class

    return decorator


# worker info
class Worker:
    def __init__(self):
        self.queue = 0  # Number of requests being processed
        self.lock = Lock()  # lock for thread safety of queue_length

        self.controller_addr = None
        self.worker_addr = None
        self.name = None  # http://worker_addr/name

        self.api_instance = None
        self.device = None

    def send_heart_beat(self):
        try:
            url = self.controller_addr + "/receive_heart_beat"
            print(f'send heart beat to {url}')
            response = requests.post(
                url=url,
                json={
                    "worker_addr": self.worker_addr,
                    "name": self.name,
                    "queue": self.queue,
                },
                timeout=5,
            )
        except Exception as e:
            pass


class WorkerInfo:
    def __init__(self, name, queue):
        self.name: List[str] = name
        self.queue: int = queue


class Controller:
    def __init__(self):
        self.workers_info = {}  # Dict[worker_addr -> WorkerInfo]

    def update_worker_status(self, worker_addr: str):
        ok = True
        try:
            response = requests.post(worker_addr + "/worker_get_status", timeout=5)
            data = response.json()
            if response.status_code != 200:
                ok = False
        except requests.exceptions.RequestException as e:
            ok = False
        if ok:  # if error, update status
            self.workers_info[worker_addr] = WorkerInfo(
                data["name"],
                data["queue"],
            )
        else:  # if error, remove it
            del self.workers_info[worker_addr]

    def receive_heart_beat(self, worker_status):
        print("receive heart beat")
        worker_addr, name, queue = (
            worker_status["worker_addr"],
            worker_status["name"],
            worker_status["queue"],
        )
        if worker_addr not in self.workers_info:  # if not exist, register the worker
            self.workers_info[worker_addr] = WorkerInfo(name, queue)
            print(f"register a new worker: {worker_addr}, workers_info {self.workers_info}\n")
        else:
            self.workers_info[worker_addr].queue = queue
        self.workers_info[worker_addr].last_heart_beat = time.time()

    def remove_stale_workers_by_expiration(self):
        expire = time.time() - 10
        to_delete = []
        for worker_addr, w_info in self.workers_info.items():
            if w_info.last_heart_beat < expire:
                to_delete.append(worker_addr)

        for worker_addr in to_delete:
            print(f"remove staled worker {worker_addr}")
            del self.workers_info[worker_addr]

    def inference(self, name, request):
        # # find best worker address
        worker_addrs = []
        worker_addr = None
        shortest_queue = 1000000
        for w_addr, w_info in self.workers_info.items():
            if w_info.name == name:
                worker_addrs.append(w_addr)
                if w_info.queue < shortest_queue:
                    shortest_queue = w_info.queue
                    worker_addr = w_addr
        assert len(worker_addrs) > 0, f"no available workers for {name}"
        # self.update_worker_status(worker_addr) # extremely affect performance 20->30
        self.workers_info[worker_addr].queue += 1
        # import random
        # worker_addr = random.choice(list(self.workers_info.keys()))

        try:
            target_url = f"{worker_addr}/{name}"
            # forward
            # copy headers, files and none-files
            # headers = {key: value for (key, value) in request.headers.items() if key not in ['Content-Length', 'Content-Type', 'Host']}
            data = request.POST
            files = request.FILES

            # forward by method
            if request.method == 'GET':
                response = requests.get(target_url, params=request.GET)
            elif request.method == 'POST':
                response = requests.post(target_url, data=data, files=files)
                # response = requests.post(target_url, data=data, files=files, headers=headers)
            elif request.method == 'PUT':
                response = requests.put(target_url, data=data)
            elif request.method == 'DELETE':
                response = requests.delete(target_url)
            else:
                return JsonResponse({'error': 'Unsupported method'}, status=405)

            return HttpResponse(response.content, status=response.status_code, content_type=response.headers['Content-Type'])
            # return redirect(target_url)
        except requests.exceptions.RequestException as e: # delete failed worker_addr
            print(f"remove failed worker {worker_addr}")
            del self.workers_info[worker_addr]


worker_info = Worker()

controller = Controller()


def set_is_controller(_is_controller):
    global is_controller
    is_controller = _is_controller


def initialize_all():
    global is_controller
    global scheduler
    if is_controller:
        scheduler.add_job(controller.remove_stale_workers_by_expiration, trigger="interval", seconds=10)
    else:
        worker_info.api_instance = registered_apis[worker_info.name]()
        worker_info.api_instance.init(worker_info.device)
        worker_info.send_heart_beat()
        scheduler.add_job(worker_info.send_heart_beat, trigger="interval", seconds=8)


def api_inference(name, request):
    global worker_info
    if is_controller:
        return controller.inference(name, request)  # redirect
    else:
        with worker_info.lock:
            worker_info.queue += 1
        try:
            with worker_info.lock: # NOTE: important for complex codes to avoid unexpected behaviors
                response = worker_info.api_instance.inference(request)
        finally:
            with worker_info.lock:
                worker_info.queue -= 1
        return response


# for worker
def api_get_status(request):
    return JsonResponse(
        {
            "name": worker_info.name,
            "queue": worker_info.queue,
        }
    )


def receive_heart_beat(request):
    # global controller
    raw_data = request.body.decode("utf-8")
    data = json.loads(raw_data)
    controller.receive_heart_beat(data)
    return JsonResponse({})

def page(request):
    return render(request, 'index.html')
