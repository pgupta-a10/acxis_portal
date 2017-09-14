from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer

class JSONResponse(HttpResponse):
	"""
		An HttpResponse that renders it's content into JSON.
	"""

	def __init__(self, data, **kwargs):
		content = JSONRenderer().render(data)
		kwargs['content_type'] = 'application/json'
		super(JSONResponse, self).__init__(content, **kwargs)


class NoPermResponse(HttpResponse):
	"""Shortcut for returning an HTTP 403 Permission Denied response"""
	def __init__(self, **kwargs):
		self.status_code = 403
		super(NoPermResponse, self).__init__(None, **kwargs)