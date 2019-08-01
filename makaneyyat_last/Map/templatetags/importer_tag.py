from django import template

register = template.Library()

@register.simple_tag
def filter_headers(header):
    id = header[0]
    title = header[1]
    relation = header[14]
    return [id,title,relation]

@register.simple_tag
def filter_rows(rows):
    return [rows[0],rows[1],rows[14]]