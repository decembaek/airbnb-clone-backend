from django.urls import path

from . import views


urlpatterns = [
    path("", views.Wishlists.as_view()),
    path("<int:pk>", views.WishlistDetail.as_view()),
    # pk 가 2개 이상일시 사용법
    path("<int:pk>/rooms/<int:room_pk>", views.WishlistToggle.as_view()),
]
