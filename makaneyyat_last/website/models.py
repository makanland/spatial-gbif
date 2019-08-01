from django.db import models

# New imports added for ParentalKey, Orderable, InlinePanel, ImageChooserPanel

from modelcluster.fields import ParentalKey

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index

from .utilities import TranslatedField



class HomePage(Page):

	def get_context(self, request):
		context = super(HomePage, self).get_context(request)
		sitepages = self.get_children().live()
		context["sitepages"] = sitepages
		return context

	title_ar = models.CharField(max_length=250, blank = True)
	body_en = RichTextField(blank = True)
	body_ar = RichTextField(blank = True)
	body = TranslatedField('body_en', 'body_ar')
	Title = TranslatedField('title', 'title_ar')
	
	content_panels = Page.content_panels + [FieldPanel('body_en', classname = 'full'),
	FieldPanel('body_ar', classname = 'full'), FieldPanel('title_ar'),]


class SitePage(Page):

	title_ar = models.CharField(max_length=250, blank = True)
	body_en = RichTextField(blank = True)
	body_ar = RichTextField(blank = True)
	intro_en = models.CharField(max_length = 250, blank = True )
	intro_ar = models.CharField(max_length = 250, blank = True )
	body = TranslatedField('body_en', 'body_ar')
	Title = TranslatedField('title', 'title_ar')
	intro = TranslatedField('intro_en', 'intro_ar')
	
	content_panels = Page.content_panels + [
		FieldPanel('intro_en'),
		FieldPanel('body_en', classname = 'full'),
		FieldPanel('title_ar'),
		FieldPanel('intro_ar'),
		FieldPanel('body_ar', classname = 'full'),
		InlinePanel('gallery_images', label="Gallery images"),
	]



class SitePageGalleryImage(Orderable):
    page = ParentalKey(SitePage, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)
    
    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]

