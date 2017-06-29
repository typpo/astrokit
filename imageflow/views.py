import time

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.utils.dateparse import parse_datetime

import imageflow.s3_util as s3_util
from astrometry.util import process_astrometry_online

from astrometry.models import AstrometrySubmission, AstrometrySubmissionJob
from imageflow.models import AnalysisResult, ImageFilter, UserUploadedImage

def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))

def upload_image(request):
    if request.method == 'POST':
        submissions = []
        for key in request.FILES:
            img = request.FILES[key]
            # Data is read just once to avoid rewinding.
            img_data = img.read()
            url = s3_util.upload_to_s3(img_data, 'raw', img.name)
            submission = process_astrometry_online(url)
            UserUploadedImage(user=request.user,
                              image_url=url,
                              astrometry_submission_id=submission.subid).save()
            submissions.append(submission)

        # Redirect to submission viewing page.
        return redirect('astrometry', subid=submissions[0].subid)

    return render_to_response('upload_image.html', {},
            context_instance=RequestContext(request))

def astrometry(request, subid):
    # TODO(ian): Look up submission and view status.
    # TODO(ian): Handle failed Analysis Result.
    try:
        result = AnalysisResult.objects.get( \
                astrometry_job__submission__subid=subid, \
                status=AnalysisResult.COMPLETE)
    except ObjectDoesNotExist:
        return render_to_response('submission_pending.html', {},
                context_instance=RequestContext(request))

    template_args = {
        'result': result.get_summary_obj(),
        'image_filters': ImageFilter.objects.all(),
    }
    return render_to_response('submission.html', template_args,
            context_instance=RequestContext(request))

def set_datetime(request, subid):
    try:
        result = AnalysisResult.objects.get( \
                astrometry_job__submission__subid=subid, \
                status=AnalysisResult.COMPLETE)
    except ObjectDoesNotExist:
        return JsonResponse({
            'success': False,
            'msg': 'Could not find corresponding AnalysisResult',
        })

    # Set new datetime.
    try:
        parsed_dt = parse_datetime(request.POST.get('image_datetime'))
    except ValueError:
        return JsonResponse({
            'success': False,
            'msg': 'Invalid datetime',
        })

    if not parsed_dt:
        return JsonResponse({
            'success': False,
            'msg': 'Could not parse datetime',
        })

    result.image_datetime = parsed_dt
    result.save()

    return JsonResponse({
        'success': True,
        'msg': 'Resolved input to %s' % parsed_dt.isoformat()
    })

def set_filter_band(request, subid):
    try:
        result = AnalysisResult.objects.get( \
                astrometry_job__submission__subid=subid, \
                status=AnalysisResult.COMPLETE)
    except ObjectDoesNotExist:
        return JsonResponse({
            'success': False,
            'msg': 'Could not find corresponding AnalysisResult',
        })

    band = request.POST.get('filter_band')
    if not band:
        return JsonResponse({
            'success': False,
            'msg': 'Filter band not specified',
        })

    try:
        filter_band = ImageFilter.objects.get(band=band)
    except ObjectDoesNotExist:
        return JsonResponse({
            'success': False,
            'msg': 'Invalid filter band',
        })

    result.image_filter = filter_band
    result.save()

    return JsonResponse({
        'success': True,
        'msg': 'Resolved input to %s' % str(filter_band)
    })

def point_sources(request, subid):
    # TODO(ian): Dedup this with above code.
    try:
        result = AnalysisResult.objects.get( \
                astrometry_job__submission__subid=subid, \
                status=AnalysisResult.COMPLETE)
    except ObjectDoesNotExist:
        return render_to_response('submission_pending.html', {},
                context_instance=RequestContext(request))

    template_args = {
        'result': result.get_summary_obj(),
    }
    return render_to_response('point_sources.html', template_args,
            context_instance=RequestContext(request))

def reference_stars(request, subid):
    # TODO(ian): Dedup this with above code.
    try:
        result = AnalysisResult.objects.get( \
                astrometry_job__submission__subid=subid, \
                status=AnalysisResult.COMPLETE)
    except ObjectDoesNotExist:
        return render_to_response('submission_pending.html', {},
                context_instance=RequestContext(request))

    template_args = {
        'result': result.get_summary_obj(),
        'image_filters': ImageFilter.objects.all(),
    }
    return render_to_response('reference_stars.html', template_args,
            context_instance=RequestContext(request))

def reduction(request, subid):
    # TODO(ian): Dedup this with above code.
    try:
        result = AnalysisResult.objects.get( \
                astrometry_job__submission__subid=subid, \
                status=AnalysisResult.COMPLETE)
    except ObjectDoesNotExist:
        return render_to_response('submission_pending.html', {},
                context_instance=RequestContext(request))

    template_args = {
        'result': result.get_summary_obj(),
        'image_filters': ImageFilter.objects.all(),
    }
    return render_to_response('reduction.html', template_args,
            context_instance=RequestContext(request))

def light_curve(request, subid):
    # TODO(ian): Dedup this with above code.
    try:
        result = AnalysisResult.objects.get( \
                astrometry_job__submission__subid=subid, \
                status=AnalysisResult.COMPLETE)
    except ObjectDoesNotExist:
        return render_to_response('submission_pending.html', {},
                context_instance=RequestContext(request))

    template_args = {
        'result': result.get_summary_obj(),
    }
    return render_to_response('light_curve.html', template_args,
            context_instance=RequestContext(request))

def api_get_submission_results(request, subid):
    try:
        result = AnalysisResult.objects.get( \
                astrometry_job__submission__subid=subid, \
                status=AnalysisResult.COMPLETE)
    except ObjectDoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Result not found.',
        })

    return JsonResponse({
        'success': True,
        'result': result.get_summary_obj(),
    })
