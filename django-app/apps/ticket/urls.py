from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'', views.TicketViewSet, 'ticket')

urlpatterns = router.urls

urlpatterns += [
    url(r'ics/(?P<ticket_id>\d+)/$', views.generate_ics, name='ics'),
]
