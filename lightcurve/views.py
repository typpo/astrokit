from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import get_object_or_404

from astrometry.models import AstrometrySubmission
from astrometry.process import process_astrometry_online
from corrections import get_jd_for_analysis
from imageflow.models import ImageAnalysis, Reduction, UserUploadedImage
from lightcurve.models import LightCurve
from reduction.util import find_point_by_id

def edit_lightcurve(request, lightcurve_id):
    lc = LightCurve.objects.get(id=lightcurve_id)
    images = UserUploadedImage.objects.filter(lightcurve=lc)
    sort = request.GET.get('sort')

    if sort:
        images = images.order_by("-" + sort)

    context = {
        'lightcurve': lc,
        'images': images,
    }
    return render_to_response('lightcurve.html', context,
            context_instance=RequestContext(request))

def plot_lightcurve(request, lightcurve_id):
    lc = LightCurve.objects.get(id=lightcurve_id)
    context = {
        'lightcurve': lc,
    }
    return render_to_response('lightcurve_plot.html', context,
            context_instance=RequestContext(request))

def plot_lightcurve_json(request, lightcurve_id):
    lc = LightCurve.objects.get(id=lightcurve_id)
    ret = []
    if request.GET.get('type') == 'instrumental':
        analyses = ImageAnalysis.objects.filter(useruploadedimage__lightcurve=lc) \
                                        .exclude(status=ImageAnalysis.ASTROMETRY_PENDING)
        for analysis in analyses:
            result = find_point_by_id(analysis.annotated_point_sources, analysis.target_id)
            if not result:
                continue
            ret.append({
                'analysisId': analysis.id,
                'timestamp': analysis.image_datetime,
                'timestampJd': get_jd_for_analysis(analysis),
                'result': result,
            })
    else:
        # type == 'standard'
        reductions = Reduction.objects.filter(analysis__useruploadedimage__lightcurve=lc,
                                              analysis__status=ImageAnalysis.ADDED_TO_LIGHT_CURVE,
                                              status=Reduction.COMPLETE)

        for reduction in reductions:
            result = find_point_by_id(reduction.reduced_stars, reduction.analysis.target_id)
            if not result:
                # Reduction not complete.
                continue
            ret.append({
                'analysisId': reduction.analysis.id,
                'reductionId': reduction.id,
                'timestamp': reduction.analysis.image_datetime,
                'timestampJd': get_jd_for_analysis(reduction.analysis),
                # TODO(ian): Maybe one day we can bake the target id into the URL.
                # That way you can compare your target light curve to any light
                # curve from a known object!
                'result': result,
            })

    return JsonResponse({
        'success': True,
        'results': ret,
    })

def save_observation_default(request, lightcurve_id):
    lc = get_object_or_404(LightCurve, id=lightcurve_id, user=request.user.id)
    images = lc.imageanalysis_set.all()

    lat = request.POST.get('lat')
    lng = request.POST.get('lng')
    elevation = request.POST.get('elevation')
    extinction = request.POST.get('extinction')
    target_name = request.POST.get('target')

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
        if target_name:
            # This target is looked up during the reduction step.
            image.target_name = target_name
        image.save()

    return JsonResponse({
        'success': True,
    })

def add_image_toggle(request, lightcurve_id):
    analysis_id = request.POST.get('analysis_id')

    lc = get_object_or_404(LightCurve, id=lightcurve_id, user=request.user.id)
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

def edit_lightcurve_name(request, lightcurve_id):
    name = request.POST.get('lightcurve_name')
    lc = get_object_or_404(LightCurve, id=lightcurve_id, user=request.user.id)
    lc.name = name
    lc.save()

    return JsonResponse({
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

def my_lightcurve(request):
    lc_list = LightCurve.objects.filter(user=request.user.id)
    context_list = []

    for lc in lc_list:
        images = UserUploadedImage.objects.filter(lightcurve=lc)
        context_list.append({
            'lightcurve': lc,
            'images': images,
        })

    return render_to_response('lightcurve_list.html', {"contexts": context_list},
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

    return render_to_response('lightcurve_list.html', {"contexts": context_list, "request_all": True},
            context_instance=RequestContext(request))
