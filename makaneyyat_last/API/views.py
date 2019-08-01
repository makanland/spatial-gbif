from rest_framework import status, generics, viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly, IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey

from .serializers import *
from Map.models import *
from .filters import PropertiesFilterBackend
from django.db.models import Count, F
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from haystack.generic_views import FacetedSearchView as BaseFacetedSearchView, SearchView
from haystack.query import SearchQuerySet, SQ
from haystack.inputs import Clean, Raw, Exact
from drf_haystack.serializers import HaystackSerializer
from drf_haystack.viewsets import HaystackViewSet
from drf_haystack.mixins import FacetMixin
from drf_haystack.filters import HaystackFacetFilter,HaystackHighlightFilter,HaystackAutocompleteFilter,HaystackFilter
import re
from .permissons import UserPermission
import io
from rest_framework.parsers import JSONParser
from .makaneyyat_serializer import MakaneyyaSerializer


dataElementFilterFields = ('title','subject', 'description', 'identifier',
            'ar_title', 'ar_subject', 'ar_description',
            'creator', 'publisher', 'contributor',
            'date', 'type', 'format', 'source', 
            'language', 'coverage')

class MakaneyyatPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 10000

class DataElementViewSet(viewsets.ModelViewSet):
    permission_classes = (UserPermission,)
    queryset = DataElement.objects.all()
    serializer_class = DataElementSerializer
    pagination_class = MakaneyyatPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = dataElementFilterFields


class PointViewSet(viewsets.ModelViewSet):
    permission_classes = (UserPermission,)
    pagination_class = MakaneyyatPagination
    queryset = PointDataElement.objects.all()
    serializer_class = PointSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = dataElementFilterFields

class PolygonViewSet(viewsets.ModelViewSet):
    permission_classes = (UserPermission,)
    pagination_class = MakaneyyatPagination
    queryset = PolygonDataElement.objects.all()
    serializer_class = PolygonSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = dataElementFilterFields

class MultiPolygonViewSet(viewsets.ModelViewSet):
    permission_classes = (UserPermission,)
    pagination_class = MakaneyyatPagination
    queryset = MultiPolygonDataElement.objects.all()
    serializer_class = MultiPolygonSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = dataElementFilterFields

class LineStringViewSet(viewsets.ModelViewSet):
    permission_classes = (UserPermission,)
    pagination_class = MakaneyyatPagination
    queryset = LineStringDataElement.objects.all()
    serializer_class = LineStringSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = dataElementFilterFields

class MultiLineStringViewSet(viewsets.ModelViewSet):
    permission_classes = (UserPermission,)
    pagination_class = MakaneyyatPagination
    queryset = MultiLineStringDataElement.objects.all()
    serializer_class = MultiLineStringSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = dataElementFilterFields

class MakaneyyaViewSet(viewsets.ModelViewSet):
    permission_classes = (UserPermission,)
    pagination_class = MakaneyyatPagination
    queryset = Makaneyya.objects.filter(approved=True)
    serializer_class = MakaneyyaSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('title', 'description', 'author', 'date')
    authentication_classes = (SessionAuthentication,)





    # def list(self):
    #     queryset = self.filter_queryset(self.get_queryset())
    #
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)


class CategoriesListViewSet(viewsets.ModelViewSet):


    def list(self, request):

        categories = {
        'source' : 'source_id',
        'subject' : 'subject_id',
        'level1' : 'clc_level1',
        'level2' : 'clc_level2',
        'level3' : 'clc_level3',
        'level4' : 'clc_level4',
        'year' : 'year'
        }
        catName = request.GET.get('category')
        queryset = DataElement.objects.values(categories[catName]).annotate(total=Count('*'), categoryId = F(categories[catName]+'__id'), categoryName = F(categories[catName]+'__title')).exclude(categoryName__isnull=True).exclude(categoryId__exact = 1)
        serializer_class = CategoriesSerializer
        filter_backends = (DjangoFilterBackend,)
        filter_fields = dataElementFilterFields
        serializer = CategoriesSerializer(queryset, many=True)
        return Response(serializer.data)





class DataElementMergeViewSet(HaystackViewSet):
    permission_classes = (UserPermission,)
    pagination_class = MakaneyyatPagination
    index_models = [DataElement, PointDataElement, PolygonDataElement, MultiPolygonDataElement,
    LineStringDataElement, MultiLineStringDataElement]
    # pagination_class = PageNumberPagination
    serializer_class = DataElementMergeSerializer
    filter_backends = (HaystackFilter,)
    filter_fields = dataElementFilterFields


    def list(self, request):

        categories = {
        'source' : 'source_id__in',
        'subject' : 'subject_id__in',
        'level1' : 'clclevel1_id__in',
        'level2' : 'clclevel2_id__in',
        'level3' : 'clclevel3_id__in',
        'level4' : 'clclevel4_id__in',
        'year' : 'year_id__in'
        }
        sqs = SearchQuerySet().models(DataElement, PointDataElement, PolygonDataElement, MultiPolygonDataElement, LineStringDataElement, MultiLineStringDataElement)
        for category in categories:
            temp = request.GET.get(category)

            if temp == None:
                continue;

            tempModel = None
            if(category == 'source'):
                tempModel = Source()
            elif(category == 'subject'):
                tempModel = Subject()
            elif(category == 'level1'):
                tempModel = CLCLevel1()
            elif(category == 'level2'):
                tempModel = CLCLevel2()
            elif(category == 'level3'):
                tempModel = CLCLevel3()
            elif(category == 'level4'):
                tempModel = CLCLevel4()
            elif(category == 'year'):
                tempModel = Year()

            param_values = re.split("___",temp)
            temp_values = []
            queryset = tempModel.__class__.objects.filter(id__in = param_values).all()
            serializer = CategorySerializer(queryset, many=True)
            for d in serializer.data:
                temp_values.append(Clean(d['title']))
            sqs = sqs.filter_and(**{category+'__in':temp_values})\
                .facet('source').facet('subject').facet('level1').facet('level2').facet('level3').facet('level4').facet('year')

        facet_counts = sqs.facet_counts()
        for category in categories:
            sqs.facet(category)
        sqs_count = sqs.count()



        page = self.paginate_queryset(sqs)
        if page is not None:
            serializer = DataElementMergeSerializer(page, many=False)


            return Response(OrderedDict([
                                ("count", sqs_count),
                                ("next", None),
                                ("previous", None),
                                ("facet_count",facet_counts),
                                ("results", serializer.data)
                            ]))


        serializer = DataElementMergeSerializer(sqs, many=False)
        latest = OrderedDict([
            ("count", sqs_count),
            ("next", None),
            ("previous", None),
            ("facet_count",facet_counts.fields),
            ("results", serializer.data)
        ])
        return Response(latest)

