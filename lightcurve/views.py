from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from imageflow.models import ImageAnalysis, UserUploadedImage
from lightcurve.models import LightCurve

from astrometry.process import process_astrometry_online

def edit_lightcurve(request, lightcurve_id):
    lc = LightCurve.objects.get(id=lightcurve_id)
    images = UserUploadedImage.objects.filter(lightcurve=lc)
    context = {
        'lightcurve': lc,
        'images': images,
    }
    return render_to_response('lightcurve.html', context,
            context_instance=RequestContext(request))

def submit_astrometry(request, uploaded_image_id):
    image = UserUploadedImage.objects.get(id=uploaded_image_id)
    if hasattr(image, 'submission'):
        return JsonResponse({
            'success': True,
            'subid': image.submission.id,
        })
    image.submission = process_astrometry_online(image.image_url)
    image.save()
    return JsonResponse({
        'success': True,
        'subid': image.submission.id,
    })
