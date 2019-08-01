from django.conf import settings
import os


shp_files_dir = os.path.abspath(os.path.join(settings.BASE_DIR, 'Map', 'data' , 'shpFiles'))


def saveMemoryFile(file, file_name , extension = 'shp'):
	try:
		with open(os.path.join(shp_files_dir , file_name + '.' + extension) , '+a') as new_file:
			for chunk in file.chunks():
				new_file.write(chunk)		
			return new_file
	except:
		with open(os.path.join(shp_files_dir , file_name + '.' + extension) , '+ab') as new_file:
			for chunk in file.chunks():
				new_file.write(chunk)		
			return new_file
