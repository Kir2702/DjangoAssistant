from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('authorization', views.authorization, name='authorization'),
    path('generator', views.generator, name='generator'),
    path('samples', views.samples, name='samples'),
    path('about', views.about, name='about')

]

