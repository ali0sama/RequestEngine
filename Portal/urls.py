from rest_framework.routers import DefaultRouter
from .views import AccessRequestViewSet, ApplicationViewSet

router = DefaultRouter()
router.register("requests", AccessRequestViewSet, basename="accessrequest")
router.register("applications", ApplicationViewSet, basename="application")

urlpatterns = router.urls
