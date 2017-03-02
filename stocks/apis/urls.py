from .views import Stockapiview

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'v2', Stockapiview, base_name='stocks')
urlpatterns = router.urls





