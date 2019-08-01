import os
from .layermapping import ShpMapper
from Map.importer.jsonimporter import JsonImporter

def loadShpFile(fileName, user):
	shpFile = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'shpFiles', fileName + ".shp"))
	lm = ShpMapper(shpFile)
	lm.save()



def loadJsonFile(fileName,userid,makaneyya=None):
	jsonFile = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'shpFiles', fileName + ".geojson"))
	lm = JsonImporter(jsonFile)
	lm.save(makaneyya)