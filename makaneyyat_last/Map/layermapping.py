from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal import DataSource, OGRGeomType
from django.db import transaction
from .models import *
from django.db.models import Q

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
    'contributor': 'contributor',
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


class ShpMapper():

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

    def updateNewRecords(self):
        print("updating.....")
        sourcesMap = {}
        subjectsMap = {}
        yearsMap = {}
        clclevel1sMap = {}
        clclevel2sMap = {}
        clclevel3sMap = {}
        clclevel4sMap = {}
        clcsMap = {}

        queryset = Source.objects.all()
        for source in queryset:
            sourcesMap[source.title] = source
        queryset = Subject.objects.all()
        for subject in queryset:
            subjectsMap[subject.title] = subject
        queryset = Year.objects.all()
        for year in queryset:
            yearsMap[year.title] = year
        queryset = CLCLevel1.objects.all()
        for clclevel1 in queryset:
            clclevel1sMap[clclevel1.title] = clclevel1
        queryset = CLCLevel2.objects.all()
        for clclevel2 in queryset:
            clclevel2sMap[clclevel2.title] = clclevel2
        queryset = CLCLevel3.objects.all()
        for clclevel3 in queryset:
            clclevel3sMap[clclevel3.title] = clclevel3
        queryset = CLCLevel4.objects.all()
        for clclevel4 in queryset:
            clclevel4sMap[clclevel4.title] = clclevel4
        queryset = CORINELandCover.objects.all()
        for clc in queryset:
            clcsMap[clc.id] = clc

        # Check if new source and update sources list
        queryset = DataElement.objects.filter(source_id__isnull=True)

        for q in queryset:
            if (q.source is not None and q.source not in sourcesMap):
                newSource = Source(title=q.source)
                newSource.save()
                sourcesMap = {}
                queryset = Source.objects.all()
                for source in queryset:
                    sourcesMap[source.title] = source

        # Check if new subject and update subjects list
        queryset = DataElement.objects.filter(subject_id__isnull=True)

        for q in queryset:
            if (q.subject is not None and q.subject not in subjectsMap):
                newSubject = Subject(title=q.subject)
                newSubject.save()
                subjectsMap = {}
                queryset = Subject.objects.all()
                for subject in queryset:
                    subjectsMap[subject.title] = subject

        # Check if new year and update years list
        queryset = DataElement.objects.filter(year__isnull=True)

        for q in queryset:
            if (q.date is not None and str(q.date.year) not in yearsMap):
                newYear = Year(title=q.date.year)
                newYear.save()
                yearsMap = {}
                queryset = Year.objects.all()
                for year in queryset:
                    yearsMap[year.title] = year

        # Start Mapping and updating
        DataElement.objects.filter(source__isnull=True, source_id__isnull=True).update(
            source_id=sourcesMap["AutoGenerated"])

        for source in sourcesMap:
            print(DataElement.objects.filter(source__exact=sourcesMap[source].title, source_id__isnull=True).count())
            DataElement.objects.filter(source__exact=sourcesMap[source].title, source_id__isnull=True).update(
                source_id=sourcesMap[source])

        DataElement.objects.filter(subject__isnull=True, subject_id__isnull=True).update(
            subject_id=subjectsMap["AutoGenerated"])

        for subject in subjectsMap:
            print(
                DataElement.objects.filter(subject__exact=subjectsMap[subject].title, subject_id__isnull=True).count())
            DataElement.objects.filter(subject__exact=subjectsMap[subject].title, subject_id__isnull=True).update(
                subject_id=subjectsMap[subject])

        DataElement.objects.filter(date__isnull=True, year__isnull=True).update(year=yearsMap["AutoGenerated"])

        for year in yearsMap:
            if yearsMap[year].title != "AutoGenerated":
                print(DataElement.objects.filter(date__year=int(yearsMap[year].title), year__isnull=True).count())
                DataElement.objects.filter(date__year=int(yearsMap[year].title), year__isnull=True).update(
                    year=yearsMap[year])

        # update clc_levels to AutoGenerated only if clc is Null
        DataElement.objects.filter(clc__isnull=True).update(clc_level1=clclevel1sMap["AutoGenerated"],
                                                            clc_level2=clclevel2sMap["AutoGenerated"],
                                                            clc_level3=clclevel3sMap["AutoGenerated"],
                                                            clc_level4=clclevel4sMap["AutoGenerated"])
        # otherwise
        for clc in clcsMap:
            print(DataElement.objects.filter(clc__exact=clcsMap[clc].id).filter(
                Q(clc_level1__isnull=True) | Q(clc_level2__isnull=True) | Q(clc_level3__isnull=True) | Q(
                    clc_level4__isnull=True)).count())
            DataElement.objects.filter(clc__exact=clcsMap[clc].id).filter(
                Q(clc_level1__isnull=True) | Q(clc_level2__isnull=True) | Q(clc_level3__isnull=True) | Q(
                    clc_level4__isnull=True)).update(clc_level1=clclevel1sMap[clcsMap[clc].level1],
                                                     clc_level2=clclevel2sMap[clcsMap[clc].level2],
                                                     clc_level3=clclevel3sMap[clcsMap[clc].level3],
                                                     clc_level4=clclevel4sMap[clcsMap[clc].level4 if (
                                                                 clcsMap[clc].level4 != '') else "AutoGenerated"])

        print("finished updating...")

    # queryset = DataElement.objects.filter(Q(clc_level1__isnull = True) | Q(clc_level2__isnull = True) | Q(clc_level3__isnull = True) | Q(clc_level4__isnull = True))
    #
    # print (queryset.count())
    # print (clcsMap)
    # for q in queryset:
    # 	if(q.clc is None or q.clc.id is None):
    # 		q.clc_level1 = clclevel1sMap["AutoGenerated"]
    # 		q.clc_level2 = clclevel2sMap["AutoGenerated"]
    # 		q.clc_level3 = clclevel3sMap["AutoGenerated"]
    # 		q.clc_level4 = clclevel4sMap["AutoGenerated"]
    # 	else:
    # 		print (clcsMap[q.clc.id])
    # 		if clcsMap[q.clc.id].level1 in clclevel1sMap:
    # 			q.clc_level1 = clclevel1sMap[clcsMap[q.clc.id].level1]
    # 		else:
    # 			q.clc_level1 = clclevel1sMap["AutoGenerated"]
    #
    # 		if clcsMap[q.clc.id].level2 in clclevel2sMap:
    # 			q.clc_level2 = clclevel2sMap[clcsMap[q.clc.id].level2]
    # 		else:
    # 			q.clc_level2 = clclevel2sMap["AutoGenerated"]
    #
    # 		if clcsMap[q.clc.id].level3 in clclevel3sMap:
    # 			q.clc_level3 = clclevel3sMap[clcsMap[q.clc.id].level3]
    # 		else:
    # 			q.clc_level3 = clclevel3sMap["AutoGenerated"]
    #
    # 		if clcsMap[q.clc.id].level4 in clclevel4sMap:
    # 			q.clc_level4 = clclevel4sMap[clcsMap[q.clc.id].level4]
    # 		else:
    # 			q.clc_level4 = clclevel4sMap["AutoGenerated"]
    # 	q.save()

    def save(self, verbose=True):
        lm = LayerMapping(self.model, self.shpFile, self.mapping, transaction_mode='autocommit')
        lm.save(strict=True, verbose=verbose)
        ShpMapper.updateNewRecords()
