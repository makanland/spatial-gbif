from .layermapping import LayerMapping
from django.contrib.gis.gdal import DataSource, OGRGeomType
from django.db import transaction
from Map.models import *
from django.db.models import Q
from django.contrib.auth.models import User

mappingScheme = {
    'title': 'title',
    'ar_title': 'ar_title',
    'subject': 'subject',
    'ar_subject': 'ar_subject',
    'source': 'source',
    'ar_source': 'ar_source',
    'language': 'language',
    'description': 'descriptio',
    'ar_description': 'ar_descrip',
    'creator': 'creator',
    'ar_creator': 'ar_creator',
    'publisher': 'publisher',
    'ar_publisher': 'ar_publish',
    'contributor': 'contributo',
    'ar_contributor': 'ar_contrib',
    'type': 'type',
    'ar_type': 'ar_type',
    'format': 'format',
    'ar_format': 'ar_format',
    'relation': 'relation',
    'ar_relation': 'ar_relatio',
    'coverage': 'coverage',
    'rights': 'rights',
    'ar_rights': 'ar_rights',
    'date': 'date',
    'clc': {
        'id': 'CLCode',
    },
}


class JsonImporter():

    def __init__(self, shpFile):
        self.shpFile = shpFile
        self.layer = self.getLayer()
        self.model = self.getModel(self.layer)
        self.mapping = self.prepareMapping(self.layer, mappingScheme)


    def prepareMapping(self, layer, scheme):
        """
        this method filters the mappingScheme by removing the entries that are allowed to be null
        and does not exist in the OGR layer
        """
        mapping = {}
        mapping['geometry'] = layer.geom_type.name
        for field_name, layer_field in mappingScheme.items():
            field = self.getModel(layer)._meta.get_field(field_name)
            if isinstance(layer_field, dict):
                subMapping = {}
                layer_fields = layer_field
                for rel_field_name, layer_field in layer_fields.items():
                    if layer_field in layer.fields:
                        subMapping[rel_field_name] = layer_field
                if subMapping:
                    mapping[field_name] = subMapping
            elif layer_field in layer.fields:
                mapping[field_name] = layer_field
            if not field.null and field_name not in mapping:
                raise ValueError('%s does not exist on layer' % layer_field)
        return mapping

    def getModel(self, layer):
        if layer.geom_type.name == OGRGeomType('Multipolygon').name:
            return MultiPolygonDataElement
        elif layer.geom_type.name == OGRGeomType('Polygon').name:
            return PolygonDataElement
        elif layer.geom_type.name == OGRGeomType('Point').name:
            return PointDataElement
        elif layer.geom_type.name == OGRGeomType('Linestring').name:
            return LineStringDataElement
        elif layer.geom_type.name == OGRGeomType('MultiLinestring').name:
            return MultiLineStringDataElement
        else:
            raise TypeError('unkwown geometry type!')

    def getLayer(self, index=0):
        ds = DataSource(self.shpFile)
        if (len(ds) <= index):
            raise ValueError('DataSource\'s requested layer is out of range!')
        layer = ds[index]
        return layer

    def save(self,makaneyya, verbose=True):
        if makaneyya:
            # get lat and lon for first polygon to center makaneyya
            makaneyya.lat = self.getLayer().get_geoms()[0].coords[0][0][0]
            makaneyya.lon = self.getLayer().get_geoms()[0].coords[0][0][1]
            makaneyya.save()
            lm = LayerMapping(self.model, self.shpFile, self.mapping, transaction_mode='autocommit',makaneyya=makaneyya)
            lm.save(strict=True, verbose=verbose)
        else:
            lm = LayerMapping(self.model, self.shpFile, self.mapping, transaction_mode='autocommit')
            lm.save(strict=True, verbose=verbose)
