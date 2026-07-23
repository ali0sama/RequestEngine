from django.urls import path
from . import views
# urlpatterns = [
#     path('',),
# ]
urlpatterns = [
    path('',views.home,name='Portal-Home')
]
