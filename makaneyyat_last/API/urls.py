from django.conf.urls import url, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()

router.register(r'dataElements', DataElementViewSet)
router.register(r'pointDataElements', PointViewSet)
# router.register(r'^pointDataElements/(?P<id>.+)/$', PointViewSet.as_view())
router.register(r'polygonDataElements', PolygonViewSet)
router.register(r'multiPolygonDataElements', MultiPolygonViewSet)
router.register(r'lineStringDataElements', LineStringViewSet)
router.register(r'multiLineStringDataElements', MultiLineStringViewSet)
router.register(r'makaneyyat', MakaneyyaViewSet)
# router.register(r'search', DataElementSearchViewSet, base_name="DataElement-search")
router.register(r'dataElementsMerge', DataElementMergeViewSet, base_name="DataElement-Merge")
router.register(r'categories', CategoriesListViewSet, base_name="Categories-List")

urlpatterns = [
    url(r'^', include(router.urls)),
]