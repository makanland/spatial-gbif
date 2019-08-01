from django.contrib.gis.db import models
from django.contrib.gis import geos
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from django.utils import timezone
from taggit.managers import TaggableManager

class Source(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=2000, null=False, blank=False)

    def __str__(self):
        return str(self.title)    
    
class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=2000, null=False, blank=False)
    
    def __str__(self):
        return str(self.title)

class Year(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return str(self.title)

class CLCLevel1(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return str(self.title)

class CLCLevel2(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return str(self.title)

class CLCLevel3(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return str(self.title)

class CLCLevel4(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return str(self.title)    

# Create your models here.
class CORINELandCover(models.Model):
    id = models.IntegerField(primary_key = True)
    level1 = models.CharField(max_length = 100)
    level2 = models.CharField(max_length = 100)
    level3 = models.CharField(max_length = 100)
    level4 = models.CharField(max_length = 100, null=True, blank=True)

    def __str__(self):
        return str(self.id)


class DataElement(models.Model):

    title = models.CharField(max_length=500, null=True, blank=True)
    subject = models.CharField(max_length=500, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    creator =models.CharField(max_length=500, null=True, blank=True)
    publisher = models.CharField(max_length=500, null=True, blank=True)
    contributor = models.CharField(max_length=500, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    type = models.CharField(max_length=500, null=True, blank=True)
    format = models.CharField(max_length=500, null=True, blank=True)
    source = models.CharField(max_length=500, null=True, blank=True)
    language = models.CharField(max_length=500, null=True, blank=True)
    coverage = models.CharField(max_length=500, null=True, blank=True)
    rights = models.CharField(max_length=500, null=True, blank=True)
    relation = models.CharField(max_length=500, null=True, blank=True)
    identifier = models.CharField(max_length=500, null=True, blank=True)

    ar_title = models.CharField(max_length=500, null=True, blank=True)
    ar_subject = models.CharField(max_length=500, null=True, blank=True)
    ar_description = models.CharField(max_length=500, null=True, blank=True)

    ar_publisher = models.CharField(max_length=500, null=True, blank=True)
    ar_creator = models.CharField(max_length=500, null=True, blank=True)
    ar_contributor = models.CharField(max_length=500, null=True, blank=True)
    ar_format = models.CharField(max_length=500, null=True, blank=True)
    ar_relation = models.CharField(max_length=500, null=True, blank=True)
    ar_type = models.CharField(max_length=500, null=True, blank=True)
    ar_coverage = models.CharField(max_length=500, null=True, blank=True)


    ar_source = models.CharField(max_length=500, null=True, blank=True)
    ar_rights = models.CharField(max_length=500, null=True, blank=True)

    clc = models.ForeignKey(CORINELandCover, on_delete = models.CASCADE, null=True, blank=True) 
    clc_level1 = models.ForeignKey(CLCLevel1, on_delete = models.CASCADE, null=True, blank=True)
    clc_level2 = models.ForeignKey(CLCLevel2, on_delete = models.CASCADE, null=True, blank=True)
    clc_level3 = models.ForeignKey(CLCLevel3, on_delete = models.CASCADE, null=True, blank=True)
    clc_level4 = models.ForeignKey(CLCLevel4, on_delete = models.CASCADE, null=True, blank=True)

    source_id = models.ForeignKey(Source, on_delete = models.CASCADE, null=True, blank=True)
    subject_id = models.ForeignKey(Subject, on_delete = models.CASCADE, null=True, blank=True)
    year = models.ForeignKey(Year, on_delete = models.CASCADE, null=True, blank=True)
    
    properties = JSONField(null=True, blank=True)

    # @property
    # def identifier(self):
    #     return self.id

    @property
    def related(self):
        """this proprty represent all related dataelements e.i. dataelements
        which exist in the same makaneyya"""
        return []

    def __str__(self):
        return str(self.id)



class PointDataElement(DataElement):
    geometry = models.PointField()

    @property
    def related(self):
        """this proprty represent all related dataelements e.i. dataelements
        which exist in the same makaneyya"""
        return []

    def __str__(self):
        return str(self.id)

class PolygonDataElement(DataElement):
    geometry = models.PolygonField()
    @property
    def related(self):
        """this proprty represent all related dataelements e.i. dataelements
        which exist in the same makaneyya"""
        return []

    def __str__(self):
        return str(self.id)

class MultiPolygonDataElement(DataElement):
    geometry = models.MultiPolygonField()

    @property
    def related(self):
        """this proprty represent all related dataelements e.i. dataelements
        which exist in the same makaneyya"""
        return []

    def __str__(self):
        return str(self.id)

class LineStringDataElement(DataElement):
    geometry= models.LineStringField()

    @property
    def related(self):
        """this proprty represent all related dataelements e.i. dataelements
        which exist in the same makaneyya"""
        return []

    def __str__(self):
        return str(self.id)

class MultiLineStringDataElement(DataElement):
    geometry = models.MultiLineStringField()
    
    @property
    def related(self):
        """this proprty represent all related dataelements e.i. dataelements
        which exist in the same makaneyya"""
        return []

    def __str__(self):
        return str(self.id)

class Makaneyya(models.Model):
    description = models.TextField(max_length = 1000,blank = True)
    title = models.CharField(max_length=100)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='makaneyyatCreated',default=1)
    date = models.DateTimeField(default=timezone.now)
    lastEdited = models.DateTimeField(auto_now = True)
    approved = models.BooleanField(default=False)
    lon = models.FloatField('longitude', null=True, blank=True, default=32.223516)
    lat = models.FloatField('latitude', null=True, blank=True, default=35.239109)
    tags = TaggableManager(blank = True);
    gbifQuery = models.CharField(max_length=100000,blank = True,default='');
    gbifQueryByArea = models.CharField(max_length=500,blank = True,default='');
    isGBIFMakanyyea = models.BooleanField(default=False)

    elements = models.ManyToManyField(DataElement, blank=True, related_name='makaneyyat')
    point_elements = models.ManyToManyField(PointDataElement,blank=True, related_name='makaneyyat2')
    line_elements = models.ManyToManyField(LineStringDataElement,blank=True, related_name='makaneyyat3')
    multi_line_elements = models.ManyToManyField(MultiLineStringDataElement,blank=True, related_name='makaneyyat4')
    polygon_elements = models.ManyToManyField(PolygonDataElement,blank=True, related_name='makaneyyat5')
    multi_polygon_elements = models.ManyToManyField(MultiPolygonDataElement,blank=True, related_name='makaneyyat6')

    @property
    def related(self):
        """this proprty represent all related dataelements e.i. dataelements
        which exist in the same makaneyya"""
        return []

    def __str__(self):
        return str(self.id)
