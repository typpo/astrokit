import time

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.utils.dateparse import parse_datetime

import imageflow.s3_util as s3_util
from astrometry.util import process_astrometry_online

from astrometry.models import AstrometrySubmission, AstrometrySubmissionJob
from imageflow.models import AnalysisResult, ImageFilter, Reduction, UserUploadedImage

def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))

def upload_image(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            testing = request.GET.get('testing', False)
            submissions = []
            for key in request.FILES:
                img = request.FILES[key]
                # Data is read just once to avoid rewinding.
                img_data = img.read()
                if not testing:
                    url = s3_util.upload_to_s3(img_data, 'raw', img.name)
                else:
                    url = "http://placehold.it/300x300"
                submission = process_astrometry_online(url, testing=testing)
                UserUploadedImage(user=request.user,
                                  image_url=url,
                                  astrometry_submission_id=submission.subid).save()
                submissions.append(submission)

            # Redirect to submission viewing page.
            return JsonResponse({
                'details': 'success',
                'redirect_url': reverse(
                    'astrometry', kwargs={'subid': submissions[0].subid})})

        return render_to_response('upload_image.html', {},
                context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('login'))

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
        parsed_dt = parse_datetime(request.POST.get('val'))
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
    analysis, filter_band = resolve_band(request, subid)
    analysis.image_filter = filter_band
    analysis.save()
    return JsonResponse({
        'success': True,
        'msg': 'Resolved input to %s' % str(filter_band)
    })

def set_color_index_1(request, subid):
    analysis, filter_band = resolve_band(request, subid)
    analysis.create_reduction_if_not_exists()
    analysis.reduction.color_index_1 = filter_band
    analysis.reduction.save()
    return JsonResponse({
        'success': True,
        'msg': 'Resolved input to %s' % str(filter_band)
    })

def set_color_index_2(request, subid):
    analysis, filter_band = resolve_band(request, subid)
    analysis.create_reduction_if_not_exists()
    analysis.reduction.color_index_2 = filter_band
    analysis.reduction.save()
    return JsonResponse({
        'success': True,
        'msg': 'Resolved input to %s' % str(filter_band)
    })

def resolve_band(request, subid):
    try:
        analysis = AnalysisResult.objects.get( \
                astrometry_job__submission__subid=subid, \
                status=AnalysisResult.COMPLETE)
    except ObjectDoesNotExist:
        raise Error('Could not find corresponding AnalysisResult')

    band = request.POST.get('val')
    if not band:
        raise Error('Filter band not specified')

    try:
        filter_band = ImageFilter.objects.get(band=band)
    except ObjectDoesNotExist:
        raise Error('Invalid filter band')

    return analysis, filter_band

def set_elevation(request, subid):
    return set_float(request, subid, 'image_elevation')

def set_latitude(request, subid):
    return set_float(request, subid, 'image_latitude')

def set_longitude(request, subid):
    return set_float(request, subid, 'image_longitude')

def set_second_order_extinction(request, subid):
    return set_float(request, subid, 'second_order_extinction', on_reduction=True)

def set_float(request, subid, attrname, on_reduction=False):
    try:
        analysis = AnalysisResult.objects.get( \
                astrometry_job__submission__subid=subid, \
                status=AnalysisResult.COMPLETE)
    except ObjectDoesNotExist:
        return JsonResponse({
            'success': False,
            'msg': 'Could not find corresponding AnalysisResult',
        })

    try:
        val = float(request.POST.get('val'))
    except ValueError:
        return JsonResponse({
            'success': False,
            'msg': 'Could not parse as float',
        })

    if on_reduction:
        setattr(analysis.reduction, attrname, val)
        analysis.reduction.save()
    else:
        setattr(analysis, attrname, val)
        analysis.save()

    return JsonResponse({
        'success': True,
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
    try:
        template_args.update({
            'reduction': result.reduction.get_summary_obj(),
        })
        return render_to_response('reduction.html', template_args,
                context_instance=RequestContext(request))
    except Reduction.DoesNotExist:
        # TODO(ian): Run reduction if necessary.
        template_args.update({
            'no_reduction': True
        })
        return render_to_response('reduction.html', template_args,
                context_instance=RequestContext(request))

def add_to_light_curve(request, subid):
    return 'not yet implemented'

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
