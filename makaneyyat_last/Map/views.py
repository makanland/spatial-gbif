from django.http import HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.models import User
from .models import *
from .forms import ImportShpFileForm,ImportJsonFileForm
from .load import loadShpFile
from .load import loadJsonFile
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from Makaneyyat.utils import *
from haystack.management.commands.update_index import Command as UpdateCommand
from haystack.management.commands.rebuild_index import Command as RebuildCommand
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

def index(request):
	return render(request, 'Map/makaneyya_view.html') 

class MakaneyyaDelete(generic.DeleteView):
    model = Makaneyya
    success_url = reverse_lazy('makaneyya-list')

@staff_member_required
def importShpFile(request, **kwargs):
    if(request.method == 'POST'):
        form = ImportShpFileForm(request.POST, request.FILES)
        if form.is_valid():
            #setting the file name 
            file_name = str(datetime.now().replace(microsecond = 0))
           
            #saving the shp file into the data/shpFiles dir 
            saveMemoryFile(file = request.FILES['shpfile'] , file_name = file_name )
            saveMemoryFile(file = request.FILES['shxfile'] , file_name = file_name , extension = 'shx' )
            saveMemoryFile(file = request.FILES['dbffile'] , file_name = file_name , extension = 'dbf' )
            saveMemoryFile(file = request.FILES['qpjfile'] , file_name = file_name , extension = 'qpj' )
            saveMemoryFile(file = request.FILES['prjfile'] , file_name = file_name , extension = 'prj' )
            
            loadShpFile(file_name, request.user.username)
            return render(request , 'Map/importShpFile.html' , {'form': ImportShpFileForm() , 'submition' : True})
        else:
            return render(request, 'Map/importShpFile.html', {'form': form, 'submition' : False, 'errors' : form.errors})
    else :
        form = ImportShpFileForm()
        return render(request , 'Map/importShpFile.html' , {'form': form})

@staff_member_required
def update_index(request,**kwargs):
    try:
        UpdateCommand().handle()
        messages.success(request,'Update Index Done')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except:
        messages.error(request, 'Error in updating index')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def rebuild_index(request):
    try:
        RebuildCommand().handle(interactive=False,batchsize=1000,workers=12)
        messages.success(request, 'Rebuild Index Done')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except:
        messages.error(request, 'Failed to rebuild index')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



@staff_member_required
def importJsonFile(request, **kwargs):
    if (request.method == 'POST'):
        form = ImportJsonFileForm(request.POST, request.FILES)
        if form.is_valid():
            # setting the file name
            file_name = str(datetime.now().replace(microsecond=0))
            saveMemoryFile(file=request.FILES['jsonfile'], file_name=file_name , extension = 'geojson')
            createMakaneyya = form.cleaned_data['createmakaneyya']

            print(str(request.FILES['jsonfile'].name) + ' ' + file_name)
            if createMakaneyya:
                kwagrs = {'title': str(request.FILES['jsonfile'].name) + ' ' + file_name,
                          'author': User.objects.get(id=request.user.id),
                          'isGBIFMakanyyea': False}

                makaneyya = Makaneyya.objects.create(**kwagrs)

                loadJsonFile(file_name, request.user,makaneyya=makaneyya)
            else:
                loadJsonFile(file_name, request.user)
            return render(request, 'Map/importJsonFile.html', {'form': ImportJsonFileForm(), 'submition': True})
        else:
            return render(request, 'Map/importJsonFile.html', {'form': form, 'submition': False, 'errors': form.errors})
    else:
        form = ImportJsonFileForm()
        return render(request, 'Map/importJsonFile.html', {'form': form})

class MakaneyyaListView(LoginRequiredMixin,generic.ListView):
    template_name = 'Map/makaneyyat_list.html'
    context_object_name = 'makaneyyat'
    login_url = '/accounts/login/?next='

    def get_queryset(self):
        result =  Makaneyya.objects.filter(approved=True)
        if self.request.GET.get("author"):
            result = result.filter(author__username__icontains = self.request.GET.get("author"))
        if self.request.GET.get("title"):
            result = result.filter(title__icontains = self.request.GET.get("title"))
        if self.request.GET.getlist("tags"):
            result = result.filter(tags__name__in = self.request.GET.getlist("tags"))
        return result

class DataElementExploreView(generic.TemplateView):
    template_name = 'Map/makaneyya_edit.html'

class MakaneyyaMapView(generic.TemplateView):
    template_name = 'Map/makaneyya_view.html'


class ExploreGBIFView(generic.TemplateView):
    template_name = 'Map/explore_gbif.html'