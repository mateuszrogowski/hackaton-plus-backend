from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^',
        views.TicketViewSet.as_view({'post': 'post', 'get': 'get'}),
        name='ticket'),
]
