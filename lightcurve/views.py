from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from imageflow.models import ImageAnalysis, UserUploadedImage
from lightcurve.models import LightCurve

from process_pending_submissions import SubmissionHandler

def edit_lightcurve(request, lightcurve_id):
    lc = LightCurve.objects.get(id=lightcurve_id)
    images = UserUploadedImage.objects.filter(lightcurve=lc)
    context = {
        'lightcurve': lc,
        'images': images,
    }
    return render_to_response('lightcurve.html', context,
            context_instance=RequestContext(request))

def create_analysis(request, uploaded_image_id):
    # Placeholder function for triggering the creation of an analysis.
    pass
