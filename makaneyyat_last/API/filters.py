from rest_framework import filters 

class PropertiesFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):

        for param in request.query_params:
            if param in  ('page', 'format','limit','offset') :
                continue
            values = request.query_params.getlist(param)
            key_qset = None
            for value in values:
                if value.isdigit():
                    value = int(value)
                key_qset =  key_qset | queryset.filter(properties__contains = {param : value}) if key_qset else queryset.filter(properties__contains = {param : value}) 

            queryset = key_qset

        return queryset.distinct()