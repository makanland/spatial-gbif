import datetime
from django import template
from django.conf import settings
from django.utils.translation import get_language_from_request

register = template.Library()


@register.simple_tag
def get_facet_terms(facets, facet):
	list = []
	for term in facets[facet]:
		list.append((term, facets[facet][term]))
	return list



@register.simple_tag
def get_collection_alias(coll):

	if coll == 'locations':
		alias = 'Land cover'
	elif coll == 'dcis':
		alias = 'Data elements'
	else:
		alias = 'Not recognized'
	return alias


# @register.inclusion_tag('tags/facets.html', takes_context=True)
# def get_facets(context):
# 	collections = [
# 		{
# 			'name': 'Filter:',
# 			'alias': 'Filters:',
# 			'info': get_collection_info('source'),
# 			'facets': [],
# 		},
# 	]
# 	for collection,coll_facets in context['collections'].items():
# 		if not coll_facets:
# 			continue
# 		coll = {
# 		'name': collection, 
# 		'alias': get_collection_alias(collection), 
# 		'info': get_collection_info(collection),
# 		'facets': []
# 		}
# 		for facet in coll_facets:
# 			facet = {'name': facet, 'terms':get_facet_terms(coll_facets, facet)}
# 			if facet['name'].lower() == 'Source'.lower():
# 				collections[0]['facets'].append(facet)
# 			else:
# 				coll['facets'].append(facet)
# 		collections.append(coll)

# 	return {
# 		# required by the pageurl tag that we want to use within this template
# 		'request': context['request'],
# 		'collections': collections,
# 	}


@register.simple_tag
def get_base_api_url():
	# return 'https://' + settings.ALLOWED_HOSTS[0] + '/API/'
	return 'http://' + settings.ALLOWED_HOSTS[0] + ':' + str(settings.PORT) + '/API/'




@register.simple_tag
def get_language(request):
	return get_language_from_request(request)


def get_collection_info(coll):

	if coll == 'locations':
		alias = 'Based on CORINE land Cover'
	elif coll == 'dcis':
		alias = 'Data elements'
	else:
		alias = ''

	return alias


