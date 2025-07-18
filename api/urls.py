from django.urls import path
from base.views import RunJobAPIView,JobStatusAPIView,JobStartAPIView,LoginAPI
urlpatterns = [
    path('run/',RunJobAPIView.as_view()),
    path('job/status/',JobStatusAPIView.as_view()),
    path('start/',JobStartAPIView.as_view()),
    path('login/',LoginAPI.as_view()),
]
