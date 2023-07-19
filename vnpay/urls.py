from django.urls import include, path

from rest_framework import routers
from . import views
from .views import VnpayViewSet

router = routers.DefaultRouter()
router.register("", views.VnpayViewSet, "vn_pay")

urlpatterns = [
    path('', include(router.urls)),
    path('payment', VnpayViewSet.as_view({
        'post': 'payment'
    })),
]