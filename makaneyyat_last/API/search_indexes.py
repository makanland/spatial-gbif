from Map.models import *
from haystack import indexes

class NonGeoDataElementIndex(indexes.ModelSearchIndex, indexes.Indexable):

	type = indexes.CharField(default = 'NON', indexed = False)
	text = indexes.CharField(document=True)
	id = indexes.CharField(model_attr = 'id')
	type = indexes.CharField(model_attr = 'type', null= True, faceted = True)
	format = indexes.CharField(model_attr = 'format', null= True, faceted = True)
	title = indexes.CharField(model_attr = 'title', null= True)
	description = indexes.CharField(model_attr = 'description', null= True)
	subject = indexes.CharField(model_attr = 'subject', null= True, faceted=True)
	date = indexes.DateField(model_attr = 'date', null= True, faceted = True)
	creator = indexes.CharField(model_attr = 'creator', null= True, faceted = True)
	publisher = indexes.CharField(model_attr = 'publisher', null= True, faceted = True)
	language = indexes.CharField(model_attr = 'language', null= True, faceted = True)
	source = indexes.CharField(model_attr='source', null= True, faceted = True)
	identifier = indexes.CharField(model_attr='identifier', null= True, faceted = True)
	level1 = indexes.CharField(model_attr='clc__level1', null= True, faceted = True)
	level2 = indexes.CharField(model_attr='clc__level2', null= True, faceted = True)
	level3 = indexes.CharField(model_attr='clc__level3', null= True, faceted = True)
	level4 = indexes.CharField(model_attr='clc__level4', null= True, faceted = True)
	source_id = indexes.CharField(model_attr='source_id__id', null=True, faceted=True)
	subject_id = indexes.CharField(model_attr='subject_id__id', null=True, faceted=True)
	clclevel1_id = indexes.CharField(model_attr='clc_level1__id', null=True, faceted=True)
	clclevel2_id = indexes.CharField(model_attr='clc_level2__id', null=True, faceted=True)
	clclevel3_id = indexes.CharField(model_attr='clc_level3__id', null=True, faceted=True)
	clclevel4_id = indexes.CharField(model_attr='clc_level4__id', null=True, faceted=True)
	year_id = indexes.CharField(model_attr='year__id', null=True, faceted=True)
	year = indexes.CharField(model_attr='year__title',null=True, faceted=True)

	def index_queryset(self, using=None):
		return DataElement.objects.filter(pointdataelement__isnull = True, 
			polygondataelement__isnull = True,
			multipolygondataelement__isnull = True,
			linestringdataelement__isnull = True, 
			multilinestringdataelement__isnull = True)

	def get_model(self):
		return DataElement



class PointDataElementIndex(indexes.ModelSearchIndex, indexes.Indexable):

	type = indexes.CharField(default = 'POINT', indexed = False)
	text = indexes.CharField(document=True)
	id = indexes.CharField(model_attr='id')
	type = indexes.CharField(model_attr = 'type', null= True, faceted = True)
	format = indexes.CharField(model_attr = 'format', null= True, faceted = True)
	title = indexes.CharField(model_attr = 'title', null= True)
	description = indexes.CharField(model_attr = 'description', null= True)
	subject = indexes.CharField(model_attr = 'subject', null= True, faceted=True)
	date = indexes.DateField(model_attr = 'date', null= True, faceted = True)
	creator = indexes.CharField(model_attr = 'creator', null= True, faceted = True)
	publisher = indexes.CharField(model_attr = 'publisher', null= True, faceted = True)
	language = indexes.CharField(model_attr = 'language', null= True, faceted = True)
	source = indexes.CharField(model_attr='source', null= True, faceted = True)
	identifier = indexes.CharField(model_attr='identifier', null= True, faceted = True)
	level1 = indexes.CharField(model_attr='clc__level1', null= True, faceted = True)
	level2 = indexes.CharField(model_attr='clc__level2', null= True, faceted = True)
	level3 = indexes.CharField(model_attr='clc__level3', null= True, faceted = True)
	level4 = indexes.CharField(model_attr='clc__level4', null= True, faceted = True)
	source_id = indexes.CharField(model_attr='source_id__id', null=True, faceted=True)
	subject_id = indexes.CharField(model_attr='subject_id__id', null=True, faceted=True)
	clclevel1_id = indexes.CharField(model_attr='clc_level1__id', null=True, faceted=True)
	clclevel2_id = indexes.CharField(model_attr='clc_level2__id', null=True, faceted=True)
	clclevel3_id = indexes.CharField(model_attr='clc_level3__id', null=True, faceted=True)
	clclevel4_id = indexes.CharField(model_attr='clc_level4__id', null=True, faceted=True)
	year_id = indexes.CharField(model_attr='year__id', null=True, faceted=True)
	year = indexes.CharField(model_attr='year__title', null=True, faceted=True)

	def get_model(self):
		return PointDataElement


class PolygonDataElementIndex(indexes.ModelSearchIndex, indexes.Indexable):

	type = indexes.CharField(default = 'POLYGON', indexed = False)
	text = indexes.CharField(document=True)
	id = indexes.CharField(model_attr='id')
	type = indexes.CharField(model_attr = 'type', null= True, faceted = True)
	format = indexes.CharField(model_attr = 'format', null= True, faceted = True)
	title = indexes.CharField(model_attr = 'title', null= True)
	description = indexes.CharField(model_attr = 'description', null= True)
	subject = indexes.CharField(model_attr = 'subject', null= True, faceted=True)
	date = indexes.DateField(model_attr = 'date', null= True, faceted = True)
	creator = indexes.CharField(model_attr = 'creator', null= True, faceted = True)
	publisher = indexes.CharField(model_attr = 'publisher', null= True, faceted = True)
	language = indexes.CharField(model_attr = 'language', null= True, faceted = True)
	source = indexes.CharField(model_attr='source', null= True, faceted = True)
	identifier = indexes.CharField(model_attr='identifier', null= True, faceted = True)
	level1 = indexes.CharField(model_attr='clc__level1', null= True, faceted = True)
	level2 = indexes.CharField(model_attr='clc__level2', null= True, faceted = True)
	level3 = indexes.CharField(model_attr='clc__level3', null= True, faceted = True)
	level4 = indexes.CharField(model_attr='clc__level4', null= True, faceted = True)
	source_id = indexes.CharField(model_attr='source_id__id', null=True, faceted=True)
	subject_id = indexes.CharField(model_attr='subject_id__id', null=True, faceted=True)
	clclevel1_id = indexes.CharField(model_attr='clc_level1__id', null=True, faceted=True)
	clclevel2_id = indexes.CharField(model_attr='clc_level2__id', null=True, faceted=True)
	clclevel3_id = indexes.CharField(model_attr='clc_level3__id', null=True, faceted=True)
	clclevel4_id = indexes.CharField(model_attr='clc_level4__id', null=True, faceted=True)
	year_id = indexes.CharField(model_attr='year__id', null=True, faceted=True)
	year = indexes.CharField(model_attr='year__title', null=True, faceted=True)

	def get_model(self):
		return PolygonDataElement


class MultiPolygonDataElementIndex(indexes.ModelSearchIndex, indexes.Indexable):

	type = indexes.CharField(default = 'MULTIPOLYGON', indexed = False)
	text = indexes.CharField(document=True)
	id = indexes.CharField(model_attr='id')
	type = indexes.CharField(model_attr = 'type', null= True, faceted = True)
	format = indexes.CharField(model_attr = 'format', null= True, faceted = True)
	title = indexes.CharField(model_attr = 'title', null= True)
	description = indexes.CharField(model_attr = 'description', null= True)
	subject = indexes.CharField(model_attr = 'subject', null= True, faceted=True)
	date = indexes.DateField(model_attr = 'date', null= True, faceted = True)
	creator = indexes.CharField(model_attr = 'creator', null= True, faceted = True)
	publisher = indexes.CharField(model_attr = 'publisher', null= True, faceted = True)
	language = indexes.CharField(model_attr = 'language', null= True, faceted = True)
	source = indexes.CharField(model_attr='source', null= True, faceted = True)
	identifier = indexes.CharField(model_attr='identifier', null= True, faceted = True)
	level1 = indexes.CharField(model_attr='clc__level1', null= True, faceted = True)
	level2 = indexes.CharField(model_attr='clc__level2', null= True, faceted = True)
	level3 = indexes.CharField(model_attr='clc__level3', null= True, faceted = True)
	level4 = indexes.CharField(model_attr='clc__level4', null= True, faceted = True)
	source_id = indexes.CharField(model_attr='source_id__id', null=True, faceted=True)
	subject_id = indexes.CharField(model_attr='subject_id__id', null=True, faceted=True)
	clclevel1_id = indexes.CharField(model_attr='clc_level1__id', null=True, faceted=True)
	clclevel2_id = indexes.CharField(model_attr='clc_level2__id', null=True, faceted=True)
	clclevel3_id = indexes.CharField(model_attr='clc_level3__id', null=True, faceted=True)
	clclevel4_id = indexes.CharField(model_attr='clc_level4__id', null=True, faceted=True)
	year_id = indexes.CharField(model_attr='year__id', null=True, faceted=True)
	year = indexes.CharField(model_attr='year__title', null=True, faceted=True)

	def get_model(self):
		return MultiPolygonDataElement



class LineStringDataElementIndex(indexes.ModelSearchIndex, indexes.Indexable):

	type = indexes.CharField(default = 'LINESTRING', indexed = False)
	text = indexes.CharField(document=True)
	id = indexes.CharField(model_attr='id')
	type = indexes.CharField(model_attr = 'type', null= True, faceted = True)
	format = indexes.CharField(model_attr = 'format', null= True, faceted = True)
	title = indexes.CharField(model_attr = 'title', null= True)
	description = indexes.CharField(model_attr = 'description', null= True)
	subject = indexes.CharField(model_attr = 'subject', null= True, faceted=True)
	date = indexes.DateField(model_attr = 'date', null= True, faceted = True)
	creator = indexes.CharField(model_attr = 'creator', null= True, faceted = True)
	publisher = indexes.CharField(model_attr = 'publisher', null= True, faceted = True)
	language = indexes.CharField(model_attr = 'language', null= True, faceted = True)
	source = indexes.CharField(model_attr='source', null= True, faceted = True)
	identifier = indexes.CharField(model_attr='identifier', null= True, faceted = True)
	level1 = indexes.CharField(model_attr='clc__level1', null= True, faceted = True)
	level2 = indexes.CharField(model_attr='clc__level2', null= True, faceted = True)
	level3 = indexes.CharField(model_attr='clc__level3', null= True, faceted = True)
	level4 = indexes.CharField(model_attr='clc__level4', null= True, faceted = True)
	source_id = indexes.CharField(model_attr='source_id__id', null=True, faceted=True)
	subject_id = indexes.CharField(model_attr='subject_id__id', null=True, faceted=True)
	clclevel1_id = indexes.CharField(model_attr='clc_level1__id', null=True, faceted=True)
	clclevel2_id = indexes.CharField(model_attr='clc_level2__id', null=True, faceted=True)
	clclevel3_id = indexes.CharField(model_attr='clc_level3__id', null=True, faceted=True)
	clclevel4_id = indexes.CharField(model_attr='clc_level4__id', null=True, faceted=True)
	year_id = indexes.CharField(model_attr='year__id', null=True, faceted=True)
	year = indexes.CharField(model_attr='year__title', null=True, faceted=True)

	def get_model(self):
		return LineStringDataElement


class MultiLineStringDataElementIndex(indexes.ModelSearchIndex, indexes.Indexable):

	type = indexes.CharField(default = 'MULTILINESTRING', indexed = False)
	text = indexes.CharField(document=True)
	id = indexes.CharField(model_attr='id')
	type = indexes.CharField(model_attr = 'type', null= True, faceted = True)
	format = indexes.CharField(model_attr = 'format', null= True, faceted = True)
	title = indexes.CharField(model_attr = 'title', null= True)
	description = indexes.CharField(model_attr = 'description', null= True)
	subject = indexes.CharField(model_attr = 'subject', null= True, faceted=True)
	date = indexes.DateField(model_attr = 'date', null= True, faceted = True)
	creator = indexes.CharField(model_attr = 'creator', null= True, faceted = True)
	publisher = indexes.CharField(model_attr = 'publisher', null= True, faceted = True)
	language = indexes.CharField(model_attr = 'language', null= True, faceted = True)
	source = indexes.CharField(model_attr='source', null= True, faceted = True)
	identifier = indexes.CharField(model_attr='identifier', null= True, faceted = True)
	level1 = indexes.CharField(model_attr='clc__level1', null= True, faceted = True)
	level2 = indexes.CharField(model_attr='clc__level2', null= True, faceted = True)
	level3 = indexes.CharField(model_attr='clc__level3', null= True, faceted = True)
	level4 = indexes.CharField(model_attr='clc__level4', null= True, faceted = True)
	source_id = indexes.CharField(model_attr='source_id__id', null=True, faceted=True)
	subject_id = indexes.CharField(model_attr='subject_id__id', null=True, faceted=True)
	clclevel1_id = indexes.CharField(model_attr='clc_level1__id', null=True, faceted=True)
	clclevel2_id = indexes.CharField(model_attr='clc_level2__id', null=True, faceted=True)
	clclevel3_id = indexes.CharField(model_attr='clc_level3__id', null=True, faceted=True)
	clclevel4_id = indexes.CharField(model_attr='clc_level4__id', null=True, faceted=True)
	year_id = indexes.CharField(model_attr='year__id', null=True, faceted=True)
	year = indexes.CharField(model_attr='year__title', null=True, faceted=True)

	def get_model(self):
		return MultiLineStringDataElement

