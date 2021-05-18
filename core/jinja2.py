from jinja2 import Environment
from django.urls import reverse
from django.contrib.staticfiles.storage import staticfiles_storage
# for more later django installations use:
# from django.templatetags.static import static
from widget_tweaks.templatetags.widget_tweaks import render_field


def environment(**options):
	env = Environment(**options)
	env.globals.update({
		"static": staticfiles_storage.url,
		"url": reverse,
        'render_field': render_field,
	})
	return env