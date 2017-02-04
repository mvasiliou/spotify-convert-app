from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^login/$', views.user_login, name = 'login'),
    url(r'^logout/$', views.user_logout, name = 'logout'),
    url(r'^sign_s3/$', views.sign_s3, name = 'sign_s3'),
    url(r'^submit_form/$', views.submit_form, name = 'submit_form'),
]