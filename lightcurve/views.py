from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from astrometry.models import AstrometrySubmission
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

def save_observation_default(request, lightcurve_id):
    lc = LightCurve.objects.get(id=lightcurve_id)
    images = lc.imageanalysis_set.all()

    lat = request.POST.get('lat')
    lng = request.POST.get('lng')
    elevation = request.POST.get('elevation')
    extinction = request.POST.get('extinction')

    print lat, lng, elevation, extinction

    for image in images:
        if lat:
            image.image_latitude= float(lat)
        if lng:
            image.image_longitude = float(lng)
        if elevation:
            image.image_elevation = float(elevation)
        if extinction:
            reduction = image.get_reduction_or_create()
            reduction.second_order_extinction = float(extinction)
            reduction.save()
        image.save()

    return JsonResponse({
        'success': True,
    })

def add_image_toggle(request, lightcurve_id):
    analysis_id = request.POST.get('analysis_id')

    lc = LightCurve.objects.get(id=lightcurve_id)
    image = lc.imageanalysis_set.get(id=analysis_id)

    if image.status == ImageAnalysis.ADDED_TO_LIGHT_CURVE:
        image.status = ImageAnalysis.REDUCTION_COMPLETE
    elif image.status == ImageAnalysis.REDUCTION_COMPLETE:
        image.status = ImageAnalysis.ADDED_TO_LIGHT_CURVE
    image.save()

    return JsonResponse({
        'added': image.status == ImageAnalysis.ADDED_TO_LIGHT_CURVE,
        'success': True,
    })

def get_status(request, lightcurve_id):
    lc = LightCurve.objects.get(id=lightcurve_id)
    images = lc.useruploadedimage_set.all()
    num_processed = sum([image.submission.is_done() for image in images if image.submission])

    return JsonResponse({
        'success': True,
        'numProcessed': num_processed,
        'complete': num_processed == len(images),
    })

def lightcurve_listing(request):
    lc_list = LightCurve.objects.filter(user=request.user.id) #request.user.id
    context_list = []

    for lc in lc_list:
        images = UserUploadedImage.objects.filter(lightcurve=lc)
        context_list.append({
            'lightcurve': lc,
            'images': images,
        })

    return render_to_response('lightcurve-listing.html', {"contexts": context_list},
            context_instance=RequestContext(request))

def all_lightcurve(request):
    lc_list = LightCurve.objects.all()
    context_list = []

    for lc in lc_list:
        images = UserUploadedImage.objects.filter(lightcurve=lc)
        context_list.append({
            'lightcurve': lc,
            'images': images,
        })

    return render_to_response('lightcurve-listing.html', {"contexts": context_list, "request_all": True},
            context_instance=RequestContext(request))