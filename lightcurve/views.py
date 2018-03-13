import json

from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import get_object_or_404

from accounts.models import UserUploadedImage
from astrometry.models import AstrometrySubmission
from astrometry.process import process_astrometry_online
from corrections import get_jd_for_analysis
from imageflow.models import ImageAnalysis, ImageAnalysisPair, ImageFilter, Reduction
from lightcurve.models import LightCurve
from reduction.util import find_point_by_id

def edit_lightcurve(request, lightcurve_id):
    lc = LightCurve.objects.get(id=lightcurve_id)
    images = UserUploadedImage.objects.filter(lightcurve=lc).order_by('analysis__image_datetime')

    # Always add 5 extra empty image pairs to the list.
    image_pairs = list(ImageAnalysisPair.objects.filter(lightcurve=lc)) + ([None] * 5)

    context = {
        'lightcurve': lc,
        'reduction': lc.get_or_create_reduction(),
        'images': images,
        'image_filters': ImageFilter.objects.all(),
        'magband_filters': ImageFilter.objects.all().exclude(band='C'),
        'image_pairs': image_pairs,
        'ci_bands': ImageFilter.objects.get_ci_bands(),
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
    magband = request.POST.get('magband')
    filter = request.POST.get('filter')

    for image in images:
        if lat:
            image.image_latitude= float(lat)
        if lng:
            image.image_longitude = float(lng)
        if elevation:
            image.image_elevation = float(elevation)
        if extinction:
            reduction = lc.get_or_create_reduction()
            reduction.second_order_extinction = float(extinction)
            reduction.save()
        if target_name:
            # This target is looked up during the reduction step.
            image.target_name = target_name
        if magband:
            lc.magband = ImageFilter.objects.get(band=magband)
        if filter:
            lc.filter = ImageFilter.objects.get(band=filter)
        lc.save()
        image.save()

    return JsonResponse({
        'success': True,
    })

def apply_photometry_settings(request, lightcurve_id):
    lc = get_object_or_404(LightCurve, id=lightcurve_id, user=request.user.id)
    template_analysis = ImageAnalysis.objects.get(pk=request.POST.get('analysisId'))
    template_settings = template_analysis.photometry_settings

    # Apply the settings from this analysis to every analysis.
    count = 0
    for analysis in lc.imageanalysis_set.all():
        settings = analysis.photometry_settings
        changed = settings.sigma_psf != template_settings.sigma_psf or \
                  settings.crit_separation != template_settings.crit_separation or \
                  settings.threshold != template_settings.threshold or \
                  settings.box_size != template_settings.box_size or \
                  settings.iters != template_settings.iters
        if changed:
            analysis.photometry_settings = template_settings
            analysis.photometry_settings.save()

            analysis.status = ImageAnalysis.PHOTOMETRY_PENDING
            analysis.save()

            count += 1

    return JsonResponse({
        'success': True,
        'numUpdated': count,
    })

def save_image_pairs(request, lightcurve_id):
    lc = get_object_or_404(LightCurve, id=lightcurve_id, user=request.user.id)
    images = lc.imageanalysis_set.all()

    ciband = request.POST.get('ciband')
    pairs = json.loads(request.POST.get('pairs'))

    if ciband:
        lc.ciband = ciband
        lc.save()

    if pairs:
        # Clear existing ImageAnalysisPairs
        ImageAnalysisPair.objects.filter(lightcurve=lc).delete()

        # Rebuild them
        for pair in pairs:
            # Exclude Nones
            if all(pair):
                analysis1 = ImageAnalysis.objects.get(pk=pair[0], user=request.user.id)
                analysis2 = ImageAnalysis.objects.get(pk=pair[1], user=request.user.id)
                ImageAnalysisPair.objects.create(lightcurve=lc, analysis1=analysis1, analysis2=analysis2)

    return JsonResponse({
        'success': True,
    })

def add_images(request, lightcurve_id):
    # Add all images that are currently eligible to be in the lightcurve.
    lc = get_object_or_404(LightCurve, id=lightcurve_id, user=request.user.id)
    analyses = lc.imageanalysis_set.filter(status=ImageAnalysis.REDUCTION_COMPLETE)

    for analysis in analyses:
        analysis.status = ImageAnalysis.ADDED_TO_LIGHT_CURVE
        analysis.save()

    return JsonResponse({
        'success': True,
        'count': len(analyses),
    })

def add_image_toggle(request, lightcurve_id):
    analysis_id = request.POST.get('analysisId')

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
    name = request.POST.get('name')
    lc = get_object_or_404(LightCurve, id=lightcurve_id, user=request.user.id)
    lc.name = name
    lc.save()

    return JsonResponse({
        'success': True,
    })

def status(request, lightcurve_id):
    lc = get_object_or_404(LightCurve, pk=lightcurve_id, user=request.user.id)

    if request.method == 'POST':
        val = request.POST.get('status')
        if val == 'REDUCTION_PENDING':
            lc.status = LightCurve.REDUCTION_PENDING
        elif val == 'PHOTOMETRY_PENDING':
            lc.status = LightCurve.PHOTOMETRY_PENDING
        else:
            return JsonResponse({
                'success': False,
                'message': 'Did not recognize status %s' % val
            })

        lc.save()
        return JsonResponse({
            'success': True,
        })
    else:
        images = lc.useruploadedimage_set.all()
        pairs = ImageAnalysisPair.objects.filter(lightcurve=lc)

        num_processed = sum([image.submission.is_done() for image in images if image.submission])
        num_photometry = sum([image.analysis.is_photometry_complete() for image in images if image.analysis])
        num_target = sum([image.analysis.target_id > 0 for image in images if image.analysis])

        num_reviewed = sum([image.analysis.is_reviewed() for image in images if image.analysis])
        num_lightcurve = sum([image.analysis.status == ImageAnalysis.ADDED_TO_LIGHT_CURVE for image in images if image.analysis])
        num_reduction_complete = sum([image.analysis.status == ImageAnalysis.REDUCTION_COMPLETE for image in images if image.analysis])

        return JsonResponse({
            'success': True,
            'status': lc.status,
            'numProcessed': num_processed,
            'numPhotometry': num_photometry,
            'numPairs': len(pairs),
            'numComparisonStars': len(lc.comparison_stars),
            'numTarget': num_target,
            'numReductionComplete': num_reduction_complete + num_lightcurve,
            'numReviewed': num_reviewed,
            'numLightcurve': num_lightcurve,
            'numImages': len(images),
        })

def run_image_reductions(request, lightcurve_id):
    lc = get_object_or_404(LightCurve, pk=lightcurve_id, user=request.user.id)
    analyses = lc.imageanalysis_set.all()
    count = 0
    for analysis in analyses:
        if analysis.target_id and analysis.target_id > 0:
            analysis.status = ImageAnalysis.REVIEW_PENDING
            analysis.save()

            reduction = analysis.get_or_create_reduction()
            reduction.status = Reduction.PENDING
            reduction.save()
            count += 1

    return JsonResponse({
        'success': True,
        'numTriggered': count,
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

    return render_to_response('lightcurve_list.html', {'contexts': context_list},
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

    return render_to_response('lightcurve_list.html', {'contexts': context_list, 'request_all': True},
            context_instance=RequestContext(request))
