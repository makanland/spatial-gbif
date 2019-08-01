from django.conf.urls import url, include
from django.conf.urls.static import static
from .views import *

app_name = 'map'
urlpatterns = [
	url(r'import/shpFile', importShpFile , name = 'shpFile-import'),
	url(r'update/index', update_index , name = 'update-index'),
	url(r'rebuild/index',rebuild_index,name='rebuild-index'),
	url(r'import/jsonFile', importJsonFile , name = 'jsonFile-import'),
	url(r'makaneyya/explore', MakaneyyaListView.as_view(), name = 'makaneyya-list'),
	url(r'makaneyya/view', MakaneyyaMapView.as_view()),
	url(r'makaneyya/create', DataElementExploreView.as_view(), name='makaneyya-create'),
	url(r'makaneyya/(?P<pk>[0-9]+)/delete/$', MakaneyyaDelete.as_view(), name='makaneyya-delete'),
	url(r'makaneyya/search', ExploreGBIFView.as_view(), name = 'gbif-search'),
	url(r'', index, name = "home"),
]