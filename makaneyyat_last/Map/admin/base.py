from Map.models import *
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
import urllib.request,json
from dateutil.parser import parse
from datetime import datetime
from import_export.admin import ImportMixin
from Map.forms import DataElementImportForm

class DataELementResource(resources.ModelResource):

    class Meta:
        model = DataElement
        exclude = ('id',)

    def get_instance(self, instance_loader, row):
        try:
            params = {}
            for key in instance_loader.resource.get_import_id_fields():
                field = instance_loader.resource.fields[key]
                params[field.attribute] = field.clean(row)
            return self.get_queryset().get(**params)
        except Exception:
            return None

    def before_import_row(self, row, **kwargs):
        if row['source']:
            try:
                source = Source.objects.get(title=row['source'].strip())
                row['source_id'] = source.id
            except:
                row['source_id'] = Source.objects.create(title=row['source'].strip()).id

        if row['subject']:
            try:
                subject = Subject.objects.get(title=row['subject'].strip())
                row['subject_id'] = subject.id
            except:
                row['subject_id'] = Subject.objects.create(title=row['subject'].strip()).id

        date = None
        if 'Date' in row:
            if isinstance(row['Date'], str):
                row["date"] = datetime.strptime(row['Date'], '%Y-%m-%d')
            date = row["date"]
        elif 'date' in row:
            if isinstance(row['date'],str):
                row["date"] = datetime.strptime(row['date'], '%Y-%m-%d')
            date = row["date"]
        if date:
            year_date = date.year
            try:
                year = Year.objects.get(title=year_date)
                row['year'] = year.id
            except:
                row['year'] = Year.objects.create(title=year_date).id

    def before_import(self,dataset,using_transactions, dry_run,file_name,user,**kwargs):
        if(kwargs.pop('is_gbif')):
            for i,row in enumerate(dataset):
                searchUrl = "https://api.gbif.org/v1/species/match"
                row = list(row)
                gbif = urllib.parse.urlencode({'name': str(row[1])})
                searchUrl = searchUrl + '?' + gbif;

                with urllib.request.urlopen(searchUrl) as url:
                    data = json.loads(url.read().decode('utf-8'))

                    if data['matchType'] != 'NONE' and data['status']!='SYNONYM':
                        row[22] = data['scientificName'] + ' || ' + "https://www.gbif.org/species/"+str(data['usageKey']);
                    elif data['matchType'] != 'NONE' and data['status']=='SYNONYM':
                        if 'speciesKey' in data: row[22] = data['canonicalName'] + ' || ' + "https://www.gbif.org/species/"+str(data['speciesKey']);
                        elif 'genusKey' in data: row[22] = data['canonicalName'] + ' || ' + "https://www.gbif.org/species/"+str(data['genusKey']);
                    else:
                        row[22] = data['matchType']
                dataset[i] = tuple(row)



class CORINELandCoverResource(resources.ModelResource):
    class Meta:
        model = CORINELandCover


class MakaneyyaModelAdmin(admin.ModelAdmin):
	list_filter = ('approved','author__username',)
	list_display = ('title', 'date', 'approved', 'author')




class CORINELandCoverAdmin(ImportExportModelAdmin):
    resource_class = CORINELandCoverResource


class YearElementFilter(admin.SimpleListFilter):
    title = 'year'
    parameter_name = 'year'

    default_value = None

    def lookups(self, request, model_admin):
        list_of_years = []
        years = Year.objects.all()
        for year in years:
            list_of_years.append((str(year.id),year.title))

        return sorted(list_of_years,key=lambda tp:tp[1])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(year_id=self.value())
        return queryset


class SubjectElementFilter(admin.SimpleListFilter):
    title = 'subject id'
    parameter_name = 'subject id'

    default_value = None

    def lookups(self, request, model_admin):
        list_of_subjects = []
        subjects = Subject.objects.all()
        for subject in subjects:
            list_of_subjects.append((str(subject.id),subject.title))

        return sorted(list_of_subjects,key=lambda tp:tp[1])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(subject_id=self.value())
        return queryset

class SourceElementFilter(admin.SimpleListFilter):
    title = 'source id'
    parameter_name = 'source id'

    default_value = None

    def lookups(self, request, model_admin):
        list_of_sources = []
        sources = Source.objects.all()
        for source in sources:
            list_of_sources.append((str(source.id),source.title))

        return sorted(list_of_sources,key=lambda tp:tp[1])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(source_id=self.value())
        return queryset

class ClcLevel1ElementFilter(admin.SimpleListFilter):
    title = 'clc level1'
    parameter_name = 'clc level1'

    default_value = None

    def lookups(self, request, model_admin):
        list_of_Level1 = []
        clclevel1 = CLCLevel1.objects.all()
        for level1 in clclevel1:
            list_of_Level1.append((str(level1.id),level1.title))

        return sorted(list_of_Level1,key=lambda tp:tp[1])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(clc_level1_id=self.value())
        return queryset

class ClcLevel2ElementFilter(admin.SimpleListFilter):
    title = 'clc level2'
    parameter_name = 'clc level2'

    default_value = None

    def lookups(self, request, model_admin):
        list_of_Level2 = []
        clclevel2 = CLCLevel1.objects.all()
        for level2 in clclevel2:
            list_of_Level2.append((str(level2.id),level2.title))

        return sorted(list_of_Level2,key=lambda tp:tp[1])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(clc_level2_id=self.value())
        return queryset

class ClcLevel3ElementFilter(admin.SimpleListFilter):
    title = 'clc level3'
    parameter_name = 'clc level3'

    default_value = None

    def lookups(self, request, model_admin):
        list_of_Level3 = []
        clclevel3 = CLCLevel3.objects.all()
        for level3 in clclevel3:
            list_of_Level3.append((str(level3.id),level3.title))

        return sorted(list_of_Level3,key=lambda tp:tp[1])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(clc_level3_id=self.value())
        return queryset


class TypeElementFilter(admin.SimpleListFilter):
    title = 'type'
    parameter_name = 'type'

    default_value = None

    def lookups(self, request, model_admin):
        return(
            ('point','Point'),
            ('polygon','Polygon'),
            ('multipolygon','MultiPolygon'),
            ('line string','Line String'),
            ('multiline string','Multiline String'),
        )

    def queryset(self, request, queryset):
        if self.value()=='point':
            return queryset.filter(
                type="Point"
            )
        if self.value()=='polygon':
            return queryset.filter(
                type='Polygon'
            )

