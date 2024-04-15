from django.urls import path

# Auth Token 로그인을 위한 함수 settings 설정도 필요
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path("", views.Users.as_view()),
    path("me", views.Me.as_view()),
    path("change-password", views.ChangePassword.as_view()),
    path("log-in", views.LogIn.as_view()),
    path("log-out", views.LogOut.as_view()),
    # Auth Token 로그인 POST username, password 요청 보내면 토큰값 리턴
    path("token-login", obtain_auth_token),  # 데이터 베이스를 사용하기 떄문에 무거워짐
    # install pyjwt 설치하기
    path("jwt-login", views.JWTLogIn.as_view()),
    path("github", views.GithubLogIn.as_view()),
    path("@<str:username>", views.PublicUser.as_view()),
]
