from django.urls import path

from . import views


urlpatterns = [
    path("photos/<int:pk>", views.PhotoDetail.as_view()),
    path("photos/get-url", views.GetUploadURL.as_view()),
]
