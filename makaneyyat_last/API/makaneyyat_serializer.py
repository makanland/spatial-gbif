from collections import OrderedDict

from rest_framework import pagination, serializers
from rest_framework.fields import SkipField
from rest_framework.relations import PKOnlyObject

from .serializers import DataElementSerializer, LineStringSerializer, MultiPolygonSerializer, MultiLineStringSerializer, PointSerializer, PolygonSerializer
from Map.models import Makaneyya


class TagSerializerField(serializers.ListField):
    child = serializers.CharField()

    def to_representation(self, data):
        return data.values_list('name', flat=True)


class ElementPagination(pagination.PageNumberPagination):
    page_size = 100


class DataElementPagination(ElementPagination):
    page_query_param = 'data_element_page'



class PointElementPagination(ElementPagination):
    page_query_param = 'point_element_page'
    page_size_query_param = 'point_element_size'

class PolygonElementPagination(ElementPagination):
    page_query_param = 'polygon_element_page'
    page_size_query_param = 'polygon_element_size'


class MultiPolygonElementPagination(ElementPagination):
    page_query_param = 'multi_polygon_element_page'
    page_size_query_param = 'multi_polygon_element_size'


class LineStringElementPagination(ElementPagination):
    page_query_param = 'line_element_page'
    page_size_query_param = 'line_element_element_size'


class MultiLineStringElementPagination(ElementPagination):
    page_query_param = 'multi_line_element_page'
    page_size_query_param = 'multi_line_element_size'


class PagindatedDataElement(serializers.Field):

    def __init__(self, serializer, paginator=None,
                 **kwargs):
        self.serializer = serializer

        self.paginator = paginator()

        super(PagindatedDataElement, self).__init__(**kwargs)

    def to_internal_value(self, data):
        if len(data) > 0:
            for i in range(len(data)):
                data[i] = int(data[i])
            return data
        return []

    def to_representation(self, data):
        # return data.values_list('name', flat=True)
        elements = data.all()
        paginator = self.paginator

        page = paginator.paginate_queryset(elements, self.context['request'])
        serializer = self.serializer(page, many=True, context={'request': self.context['request']})

        return OrderedDict([
            ("count", len(elements)),
            ("results", serializer.data)
        ])

class MakaneyyaSerializer(serializers.HyperlinkedModelSerializer):

    author = serializers.StringRelatedField(read_only = True)
    tags = TagSerializerField()
    elements = PagindatedDataElement(DataElementSerializer,DataElementPagination)
    point_elements = PagindatedDataElement(PointSerializer,PointElementPagination)
    line_elements = PagindatedDataElement(LineStringSerializer,LineStringElementPagination)
    polygon_elements = PagindatedDataElement(PolygonSerializer,PolygonElementPagination)
    multi_polygon_elements = PagindatedDataElement(MultiPolygonSerializer,MultiPolygonElementPagination)
    multi_line_elements = PagindatedDataElement(MultiLineStringSerializer,MultiLineStringElementPagination)


    class Meta:
        model = Makaneyya
        fields = ('id','title','description','lon','lat','author','date','lastEdited', 'tags','elements', 'point_elements',
                  'line_elements', 'polygon_elements', 'multi_polygon_elements', 'multi_line_elements', 'gbifQuery',
                 'gbifQueryByArea','isGBIFMakanyyea')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        instance = super(MakaneyyaSerializer, self).create(validated_data)
        instance.tags.set(*tags)
        return instance
