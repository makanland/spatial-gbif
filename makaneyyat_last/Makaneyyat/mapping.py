import sys
from decimal import Decimal, InvalidOperation as DecimalInvalidOperation

from django.contrib.gis.db.models import GeometryField
from django.contrib.gis.gdal import (
    CoordTransform, DataSource, GDALException, OGRGeometry, OGRGeomType,
    SpatialReference,
)
from django.contrib.gis.gdal.field import (
    OFTDate, OFTDateTime, OFTInteger, OFTInteger64, OFTReal, OFTString,
    OFTTime,
)
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django.db import connections, models, router, transaction
from django.utils import six
from django.utils.encoding import force_text


class DynamicLayerMapping():


    MULTI_TYPES = {1: OGRGeomType('MultiPoint'),
                   2: OGRGeomType('MultiLineString'),
                   3: OGRGeomType('MultiPolygon'),
                   OGRGeomType('Point25D').num: OGRGeomType('MultiPoint25D'),
                   OGRGeomType('LineString25D').num: OGRGeomType('MultiLineString25D'),
                   OGRGeomType('Polygon25D').num: OGRGeomType('MultiPolygon25D'),
                   }


    def __init__(self, model , data_source, encoding = 'utf-8', layer = 0, geom_field = 'geom',properties_field = 'properties', transform = True):
        self.data_source = DataSource(data_source,encoding)
        self.layer = self.data_source[layer]
        self.model = model
        self.geom_field = geom_field
        self.properties_field = properties_field
        self.transform = transform


    def save(self, **kwargs):

        for feature in self.layer:
            kwargs = self.feature_kwargs(feature)
            m = self.model(**kwargs)
            m.save()

    def make_multi(self, geom_type, model_field):
        """
        Given the OGRGeomType for a geometry and its associated GeometryField,
        determine whether the geometry should be turned into a GeometryCollection.
        """
        return (geom_type.num in self.MULTI_TYPES and
                model_field.__class__.__name__ == 'Multi%s' % geom_type.django)



    def verify_geom(self, geom, model_field):
        """
        Verifies the geometry -- will construct and return a GeometryCollection
        if necessary (for example if the model field is MultiPolygonField while
        the mapped shapefile only contains Polygons).
        """

        if self.make_multi(geom.geom_type, model_field):
            # Constructing a multi-geometry type to contain the single geometry
            multi_type = self.MULTI_TYPES[geom.geom_type.num]
            g = OGRGeometry(multi_type)
            g.add(geom)
        else:
            g = geom

        # Transforming the geometry with our Coordinate Transformation object,
        # but only if the class variable `transform` is set w/a CoordTransform
        # object.
        if self.transform:
            g.transform(self.transform)

        # Returning the WKT of the geometry.
        return g.wkt



    def feature_kwargs(self, feat):
        kwargs = {}
       
        model_geom_field = self.model._meta.get_field(self.geom_field)
        kwargs[self.geom_field] = self.verify_geom(feat.geom , model_geom_field)


        data = {}
        for field in feat.fields:
            if field.decode('utf-8') == 'id':
                continue
            data[field.decode('utf-8')] = feat.get(field.decode('utf-8'))
        kwargs[self.properties_field] = data

        return kwargs