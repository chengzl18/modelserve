"""
URL configuration for modelserve project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from modelserve import views
from modelserve.views import registered_apis, api_inference, api_get_status, receive_heart_beat, page
import functools


def generate_urlpatterns():
    global registered_apis
    urlpatterns = []
    for name in registered_apis:
        func = functools.partial(api_inference, name)
        urlpatterns.append(path(name, func))
    # for worker
    urlpatterns.append(path("worker_get_status", api_get_status))
    # for controller
    urlpatterns.append(path("receive_heart_beat", receive_heart_beat))
    urlpatterns.append(path("", page))
    
    return urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
] + generate_urlpatterns()
