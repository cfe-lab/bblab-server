from django.urls import path
from . import views

urlpatterns = [
	path('login/', views.v_login, name='v_login'),
	path('logout/', views.v_logout, name='v_logout'),
	path('', views.v_account, name='v_account'),
	path('lockout/', views.v_lockout),
]
