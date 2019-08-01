from rest_framework import serializers, pagination
from rest_framework.fields import SkipField
from rest_framework.permissions import IsAuthenticated
from rest_framework.relations import PKOnlyObject
from rest_framework_gis.serializers import GeoFeatureModelSerializer , GeoModelSerializer
from Map.models import *
from drf_haystack.serializers import HaystackSerializer, HaystackFacetSerializer
from taggit_serializer.serializers import (TagListSerializerField, TaggitSerializer)
from .search_indexes import *
import json
from collections import OrderedDict
from django.core.paginator import Paginator

dataElementFields = ('id','type','title','subject', 'description','identifier',
            'ar_title', 'ar_subject','ar_description',
            'creator','publisher', 'contributor','relation',
            'date','type','format','source', 'rights', 
            'ar_creator','ar_publisher', 'ar_contributor','ar_relation','ar_format', 'ar_source', 'ar_rights', 'ar_type',
            'language','coverage','clc', )


class CORINELandCoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = CORINELandCover
        fields = ('level1', 'level2', 'level3', 'level4')

class DataElementSerializer(serializers.HyperlinkedModelSerializer):
    clc = CORINELandCoverSerializer(read_only = True)
    class Meta:
        model = DataElement
        fields = dataElementFields

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        clc_representation = representation.pop('clc', [])
        if clc_representation:
            for key in clc_representation:
                representation[key] = clc_representation[key]
        return representation

    def to_internal_value(self, data):
        clc_internal = {}
        for key in CORINELandCoverSerializer.Meta.fields:
            if key in data:
                clc_internal[key] = data.pop(key)
        internal = super().to_internal_value(data)
        internal['clc'] = clc_internal
        return internal

class PointSerializer(GeoFeatureModelSerializer):
    clc = CORINELandCoverSerializer(read_only = True)
    class Meta:
        model = PointDataElement
        geo_field = 'geometry'
        fields = dataElementFields
        id_field = 'id'
    
    def to_representation(self, obj):
        """
        to flatten the representation of the clc field, if post request
        is performed on the api the to_internal_value(self, data) need
        to be overriden to unflatten the clc field.
        """
        representation = super().to_representation(obj)
        clc_representation = representation['properties'].pop('clc', [])
        if clc_representation: 
            for key in clc_representation:
                representation['properties'][key] = clc_representation[key]
        return representation


class PolygonSerializer(GeoFeatureModelSerializer):
    clc = CORINELandCoverSerializer(read_only = True)
    class Meta:
        model = PolygonDataElement
        geo_field = 'geometry'
        fields = dataElementFields
        id_field = 'id'
    
    def to_representation(self, obj):
        representation = super().to_representation(obj) 
        clc_representation = representation['properties'].pop('clc', [])
        if clc_representation: 
            for key in clc_representation:
                representation['properties'][key] = clc_representation[key]
        return representation


class MultiPolygonSerializer(GeoFeatureModelSerializer):
    clc = CORINELandCoverSerializer(read_only = True)
    class Meta:
        model = MultiPolygonDataElement
        geo_field = 'geometry'
        fields = dataElementFields
        id_field = 'id'

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        clc_representation = representation['properties'].pop('clc', [])
        if clc_representation: 
            for key in clc_representation:
                representation['properties'][key] = clc_representation[key]
        return representation

class LineStringSerializer(GeoFeatureModelSerializer):
    clc = CORINELandCoverSerializer(read_only = True)
    class Meta:
        model = LineStringDataElement
        geo_field = 'geometry'
        fields = dataElementFields
        id_field = 'id'

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        clc_representation = representation['properties'].pop('clc', [])
        if clc_representation: 
            for key in clc_representation:
                representation['properties'][key] = clc_representation[key]
        return representation


class MultiLineStringSerializer(GeoFeatureModelSerializer):
    clc = CORINELandCoverSerializer(read_only = True)
    class Meta:
        model = MultiLineStringDataElement
        geo_field = 'geometry'
        fields = dataElementFields
        id_field = 'id'

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        clc_representation = representation['properties'].pop('clc', [])
        if clc_representation: 
            for key in clc_representation:
                representation['properties'][key] = clc_representation[key]
        return representation



#serializer for choosing facet fields
class CategoriesSerializer(serializers.Serializer):

    categoryId = serializers.CharField(max_length=500)
    categoryName = serializers.CharField(max_length=500)
    total = serializers.CharField(max_length=100)

class CategorySerializer(serializers.Serializer):

    id = serializers.CharField(max_length=500)
    title = serializers.CharField(max_length=500)

#serializer for choosing facet fields
class DataElementMergeSerializer(serializers.Serializer):

    def to_representation(self, instance):
        return  self.serialize_sqs(instance)

    def serialize_sqs(self, queryset):
        data = {}
        serializers = {
            'PointDataElement': PointSerializer,
            'PolygonDataElement': PolygonSerializer,
            'MultiPolygonDataElement': MultiPolygonSerializer,
            'LineStringDataElement': LineStringSerializer,
            'MultiLineStringDataElement': MultiLineStringSerializer,
            'DataElement': DataElementSerializer,
        }
        segmented_qs = {'DataElement':[], 'PointDataElement': [], 'PolygonDataElement': [], 'MultiPolygonDataElement':[], 'LineStringDataElement':[], 'MultiLineStringDataElement': []}
        for res in queryset:
            for type in segmented_qs:
                if res.model.__name__ == type:
                    segmented_qs[type].append(res.object)

        for type, qs in segmented_qs.items():
            if qs:
                data[type] = serializers[type](qs, many = True).data

        return data