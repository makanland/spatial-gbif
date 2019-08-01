from django.contrib.admin.models import CHANGE, DELETION, ADDITION, LogEntry
from django.template.defaultfilters import pluralize
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from import_export.forms import ConfirmImportForm
import django
from import_export.results import RowResult
from import_export.signals import post_import

from .base import *
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text
from django.http import HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.core.urlresolvers import reverse


class DataElementAdmin(ImportExportModelAdmin):
    is_gbif = False
    resource_class = DataELementResource
    search_fields = ('title','source','creator')
    list_display = ('title','subject','source_id','year','clc_level1','clc_level2','clc_level3','creator')
    list_filter = (
        SubjectElementFilter, YearElementFilter, SourceElementFilter, TypeElementFilter, ClcLevel1ElementFilter,
        ClcLevel2ElementFilter,
        ClcLevel3ElementFilter)

    @method_decorator(require_POST)
    def process_import(self, request, *args, **kwargs):
        '''
        Perform the actual import action (after the user has confirmed he
        wishes to import)
        '''
        opts = self.model._meta
        resource = self.get_import_resource_class()(**self.get_import_resource_kwargs(request, *args, **kwargs))

        confirm_form = ConfirmImportForm(request.POST)
        if confirm_form.is_valid():
            import_formats = self.get_import_formats()
            input_format = import_formats[
                int(confirm_form.cleaned_data['input_format'])
            ]()
            kwargs.update({'is_gbif': self.is_gbif})
            tmp_storage = self.get_tmp_storage_class()(name=confirm_form.cleaned_data['import_file_name'])
            data = tmp_storage.read(input_format.get_read_mode())
            if not input_format.is_binary() and self.from_encoding:
                data = force_text(data, self.from_encoding)
            dataset = input_format.create_dataset(data)

            result = resource.import_data(dataset, dry_run=False,
                                          raise_errors=True,
                                          file_name=confirm_form.cleaned_data['original_file_name'],
                                          user=request.user,
                                          **kwargs)

            if not self.get_skip_admin_log():
                # Add imported objects to LogEntry
                logentry_map = {
                    RowResult.IMPORT_TYPE_NEW: ADDITION,
                    RowResult.IMPORT_TYPE_UPDATE: CHANGE,
                    RowResult.IMPORT_TYPE_DELETE: DELETION,
                }
                content_type_id = ContentType.objects.get_for_model(self.model).pk
                for row in result:
                    if row.import_type != row.IMPORT_TYPE_ERROR and row.import_type != row.IMPORT_TYPE_SKIP:
                        LogEntry.objects.log_action(
                            user_id=request.user.pk,
                            content_type_id=content_type_id,
                            object_id=row.object_id,
                            object_repr=row.object_repr,
                            action_flag=logentry_map[row.import_type],
                            change_message="%s through import_export" % row.import_type,
                        )

            success_message = u'Import finished, with {} new {}{} and ' \
                              u'{} updated {}{}.'.format(result.totals[RowResult.IMPORT_TYPE_NEW],
                                                         opts.model_name,
                                                         pluralize(result.totals[RowResult.IMPORT_TYPE_NEW]),
                                                         result.totals[RowResult.IMPORT_TYPE_UPDATE],
                                                         opts.model_name,
                                                         pluralize(result.totals[RowResult.IMPORT_TYPE_UPDATE]))

            messages.success(request, success_message)
            tmp_storage.remove()

            post_import.send(sender=None, model=self.model)

            url = reverse('admin:%s_%s_changelist' % self.get_model_info(),
                          current_app=self.admin_site.name)
            return HttpResponseRedirect(url)

    def import_action(self, request, *args, **kwargs):
        '''
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there where no error, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        '''
        resource = self.get_import_resource_class()(**self.get_import_resource_kwargs(request, *args, **kwargs))

        context = {}

        import_formats = self.get_import_formats()
        form = DataElementImportForm(import_formats,
                          request.POST or None,
                          request.FILES or None)

        # if request.POST and form.is_valid():
        #     self.is_gbif = form.cleaned_data['is_gbif']
        #     kwargs.update({'is_gbif':self.is_gbif})

        # resource = self.get_import_resource_class()(**self.get_import_resource_kwargs(request, *args, **kwargs))


        if request.POST and form.is_valid():
            input_format = import_formats[
                int(form.cleaned_data['input_format'])
            ]()
            import_file = form.cleaned_data['import_file']
            # pass isbgif value to resource class using kwargs
            self.is_gbif = form.cleaned_data['is_gbif']
            kwargs.update({'is_gbif': self.is_gbif})
            # first always write the uploaded file to disk as it may be a
            # memory file or else based on settings upload handlers
            tmp_storage = self.get_tmp_storage_class()()
            data = bytes()
            for chunk in import_file.chunks():
                data += chunk

            tmp_storage.save(data, input_format.get_read_mode())

            # then read the file, using the proper format-specific mode
            # warning, big files may exceed memory
            try:
                data = tmp_storage.read(input_format.get_read_mode())
                if not input_format.is_binary() and self.from_encoding:
                    data = force_text(data, self.from_encoding)
                dataset = input_format.create_dataset(data)
            except UnicodeDecodeError as e:
                return HttpResponse(_(u"<h1>Imported file has a wrong encoding: %s</h1>" % e))
            except Exception as e:
                return HttpResponse(_(u"<h1>%s encountered while trying to read file: %s</h1>" % (type(e).__name__, import_file.name)))
            result = resource.import_data(dataset, dry_run=True,
                                          raise_errors=False,
                                          file_name=import_file.name,
                                          user=request.user,**kwargs)

            context['result'] = result

            if not result.has_errors():
                context['confirm_form'] = ConfirmImportForm(initial={
                    'import_file_name': tmp_storage.name,
                    'original_file_name': import_file.name,
                    'input_format': form.cleaned_data['input_format']
                })

        if django.VERSION >= (1, 8, 0):
            context.update(self.admin_site.each_context(request))
        elif django.VERSION >= (1, 7, 0):
            context.update(self.admin_site.each_context())

        context['title'] = _("Import")
        context['form'] = form
        context['opts'] = self.model._meta
        context['fields'] = [f.column_name for f in resource.get_user_visible_fields()]

        request.current_app = self.admin_site.name
        return TemplateResponse(request, [self.import_template_name],
                                context)



class PointDataElementAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'source_id', 'year', 'clc_level1','clc_level2','clc_level3')

    list_filter = (
        SubjectElementFilter, YearElementFilter, SourceElementFilter, TypeElementFilter, ClcLevel1ElementFilter,
        ClcLevel2ElementFilter,
        ClcLevel3ElementFilter)

class PolygonDataElementAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'source_id', 'year', 'clc_level1','clc_level2','clc_level3')

    list_filter = (
        SubjectElementFilter, YearElementFilter, SourceElementFilter, TypeElementFilter, ClcLevel1ElementFilter,
        ClcLevel2ElementFilter,
        ClcLevel3ElementFilter)

class MultiPolygonDataElementAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'source_id', 'year', 'clc_level1','clc_level2','clc_level3')

    list_filter = (
        SubjectElementFilter, YearElementFilter, SourceElementFilter, TypeElementFilter, ClcLevel1ElementFilter,
        ClcLevel2ElementFilter,
        ClcLevel3ElementFilter)

class LineStringDataElementAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'source_id', 'year', 'clc_level1','clc_level2','clc_level3')

    list_filter = (
        SubjectElementFilter, YearElementFilter, SourceElementFilter, TypeElementFilter, ClcLevel1ElementFilter,
        ClcLevel2ElementFilter,
        ClcLevel3ElementFilter)

class MultiLineStringDataElementAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'source_id', 'year', 'clc_level1','clc_level2','clc_level3')

    list_filter = (
    SubjectElementFilter, YearElementFilter, SourceElementFilter, TypeElementFilter, ClcLevel1ElementFilter, ClcLevel2ElementFilter,
    ClcLevel3ElementFilter)

admin.site.register(Makaneyya, MakaneyyaModelAdmin)
admin.site.register(PolygonDataElement, PolygonDataElementAdmin)
admin.site.register(MultiPolygonDataElement, MultiPolygonDataElementAdmin)
admin.site.register(PointDataElement, PointDataElementAdmin)
admin.site.register(LineStringDataElement, LineStringDataElementAdmin)
admin.site.register(MultiLineStringDataElement, MultiLineStringDataElementAdmin)
admin.site.register(DataElement, DataElementAdmin)
admin.site.register(CORINELandCover, CORINELandCoverAdmin)
admin.site.register(Source)
admin.site.register(Subject)
admin.site.register(Year)
admin.site.register(CLCLevel1)
admin.site.register(CLCLevel2)
admin.site.register(CLCLevel3)
admin.site.register(CLCLevel4)

