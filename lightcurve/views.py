from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from imageflow.models import ImageAnalysis, UserUploadedImage
from lightcurve.models import LightCurve

def edit_lightcurve(request, lightcurve_id):
    lc = LightCurve.objects.get(id=lightcurve_id)
    analyses = ImageAnalysis.objects.filter(lightcurve=lc)
    images = UserUploadedImage.objects.filter(lightcurve=lc)
    context = {
        'lightcurve': lc,
        'analyses': analyses,
        'images': images,
    }
    return render_to_response('lightcurve.html', context,
            context_instance=RequestContext(request))
