from django import forms
from import_export.forms import ImportForm, ConfirmImportForm


class ImportShpFileForm(forms.Form):

	shpfile = forms.FileField(label = 'Select a .shp File ', required = True)
	shxfile = forms.FileField(label = 'Select a .shx File ', required = True)
	prjfile = forms.FileField(label = 'Select a .prj File ' , required = True)
	dbffile = forms.FileField(label = 'Select a .dbf File ', required = True)
	qpjfile = forms.FileField(label = 'Select a .qpj File ', required = True)

class ImportJsonFileForm(forms.Form):
	jsonfile = forms.FileField(label = 'Select a .geojson File ', required = True)
	createmakaneyya = forms.BooleanField(label='Do you want to create makaneyya?', required = False)

class DataElementImportForm(ImportForm):
	is_gbif = forms.BooleanField(label='Include GBIF data?', required = False)



