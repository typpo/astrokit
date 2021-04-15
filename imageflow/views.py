import time

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.utils.dateparse import parse_datetime

from astrometry.util import create_new_lightcurve, edit_lightcurve

from accounts.models import UserUploadedImage
from astrometry.models import AstrometrySubmission, AstrometrySubmissionJob
from imageflow.models import ImageAnalysis, ImageFilter, Reduction

def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))

def upload_image(request, lightcurve_id=None):
    if request.user.is_authenticated():
        if request.method == 'POST':
            imgs = [request.FILES[key] for key in request.FILES]
            if lightcurve_id:
                lightcurve = edit_lightcurve(request.user, imgs, lightcurve_id)
            else:
                lightcurve = create_new_lightcurve(request.user, imgs)

            # Redirect to submission viewing page.
            return JsonResponse({
                'details': 'success',
                'redirect_url': reverse('edit_lightcurve', kwargs={'lightcurve_id': lightcurve.id}),
            })

        return render_to_response('upload_image.html', {"lightcurve_id": lightcurve_id},
                context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('login'))


def astrometry(request, pk):
    # TODO(ian): Handle failed Analysis Result.
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        return render_to_response('submission_pending.html', {},
                context_instance=RequestContext(request))

    template_args = {
        'analysis': analysis.get_summary_obj(),
        'lightcurve': analysis.lightcurve,
        'image_filters': ImageFilter.objects.all(),
    }
    return render_to_response('summary.html', template_args,
            context_instance=RequestContext(request))

def set_datetime(request, pk):
    analysis = get_object_or_404(ImageAnalysis, pk=pk, user=request.user.id)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        return JsonResponse({
            'success': False,
            'msg': 'Astrometry is still pending',
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

    analysis.image_datetime = parsed_dt
    analysis.save()

    return JsonResponse({
        'success': True,
        'msg': 'Resolved input to %s' % parsed_dt.isoformat()
    })

def set_target_point_source(request, pk):
    analysis = get_object_or_404(ImageAnalysis, pk=pk, user=request.user.id)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        return JsonResponse({
            'success': False,
            'msg': 'Astrometry is still pending',
        })

    val = request.POST.get('val')
    if val == 0:
        val = None
    analysis.target_id = val
    #analysis.target_x = request.POST.get('x')
    #analysis.target_y = request.POST.get('y')
    analysis.save()
    return JsonResponse({
        'success': True,
    })

def set_filter_band(request, pk):
    analysis, filter_band = resolve_band(request, pk)
    analysis.image_filter = filter_band
    analysis.save()
    return JsonResponse({
        'success': True,
        'msg': 'Resolved input to %s' % str(filter_band)
    })

def resolve_band(request, pk):
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        raise Exception('Astrometry is still pending')

    band = request.POST.get('val')
    if not band:
        raise Exception('Filter band not specified')

    try:
        filter_band = ImageFilter.objects.get(band=band)
    except ObjectDoesNotExist:
        raise Exception('Invalid filter band')

    return analysis, filter_band

def set_elevation(request, pk):
    return set_float(request, pk, 'image_elevation')

def set_latitude(request, pk):
    return set_float(request, pk, 'image_latitude')

def set_longitude(request, pk):
    return set_float(request, pk, 'image_longitude')

def set_float(request, pk, attrname, on_reduction=False, allow_null=False):
    analysis = get_object_or_404(ImageAnalysis, pk=pk, user=request.user.id)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        return JsonResponse({
            'success': False,
            'msg': 'Astrometry is still pending',
        })

    try:
        rawval = request.POST.get('val')
        if rawval == '' and allow_null:
            val = None
        else:
            val = float(rawval)
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

def set_reduction_status(request, pk):
    # TODO(ian): Verify owner of reduction for all these ImageAnalysis fetches.
    # TODO(ian): Join this with analysis_status and remove the status attribute
    # on the Reduction model.
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        return JsonResponse({
            'success': False,
            'msg': 'Astrometry is still pending',
        })
    reduction = analysis.get_or_create_reduction()
    reduction.status = Reduction.PENDING
    reduction.save()
    return JsonResponse({
        'success': True,
        'message': 'Reduction status set to pending',
    })

def get_reduction_status(request, pk):
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        return JsonResponse({
            'success': False,
            'msg': 'Astrometry is still pending',
        })
    reduction = analysis.get_or_create_reduction()
    return JsonResponse({
        'success': True,
        'status': reduction.status,
    })

def analysis_status(request, pk):
    # TODO(ian): Constrain by user.
    analysis = get_object_or_404(ImageAnalysis, pk=pk, user=request.user.id)

    if request.method == 'POST':
        status = request.POST.get('status')
        if status == 'PHOTOMETRY_PENDING':
            analysis.status = ImageAnalysis.PHOTOMETRY_PENDING
            analysis.save()
            return JsonResponse({
                'success': True,
                'message': 'Photometry status set to pending',
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid status',
            })
    else:
        return JsonResponse({
            'success': True,
            'status': analysis.status,
        })

def photometry_params(request, pk):
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        return JsonResponse({
            'success': False,
            'msg': 'Astrometry is still pending',
        })

    val = request.POST.get('val')
    param = request.POST.get('param')

    params = analysis.get_or_create_photometry_settings()

    try:
        if param == 'aperture':
            params.phot_apertures = float(val)
        elif param == 'pixscale':
            params.pixel_scale = float(val)
        elif param == 'gain':
            params.gain = float(val)
        elif param == 'saturlevel':
            params.satur_level = int(val)
        else:
            return JsonResponse({
                'success': False,
                'msg': 'Did not recognize param',
            })
        params.save()
    except ValueError:
        return JsonResponse({
            'success': False,
            'msg': 'Invalid param format',
        })

    return JsonResponse({
        'success': True,
    })

def comparison_stars(request, pk):
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        return JsonResponse({
            'success': False,
            'msg': 'Astrometry is still pending',
        })
    reduction = analysis.get_or_create_reduction()

    if request.method == 'POST':
        '''
        ids = [int(x) for x in request.POST.getlist('ids[]')]
        reduction.comparison_star_ids = ids
        reduction.save()
        return JsonResponse({
            'success': True,
            'ids': ids,
        })
        '''
        return JsonResponse({
            'success': False,
            'message': 'Comparison stars must be set at the lightcurve level',
        })
    else:
        return JsonResponse({
            'success': True,
            'ids': analysis.get_comparison_star_ids(),
        })

def point_sources(request, pk):
    # TODO(ian): Dedup this with above code.
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        return render_to_response('submission_pending.html', {},
                context_instance=RequestContext(request))

    template_args = {
        'analysis': analysis.get_summary_obj(),
        'phot_settings': analysis.get_or_create_photometry_settings(),
        'select_target': request.GET.get('select_target') == '1',
        'cache_timestamp': int(time.time()),
    }
    return render_to_response('point_sources.html', template_args,
            context_instance=RequestContext(request))

def reference_stars(request, pk):
    # TODO(ian): Dedup this with above code.
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        return render_to_response('submission_pending.html', {},
                context_instance=RequestContext(request))

    template_args = {
        'analysis': analysis.get_summary_obj(),
        'image_filters': ImageFilter.objects.all(),
    }
    return render_to_response('reference_stars.html', template_args,
            context_instance=RequestContext(request))

def reduction(request, pk):
    # TODO(ian): Dedup this with above code.
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        return render_to_response('submission_pending.html', {},
                context_instance=RequestContext(request))

    # Next image for user to process in this light curve.
    next_image = ImageAnalysis.objects.filter(status=ImageAnalysis.REVIEW_PENDING,
                                              useruploadedimage__lightcurve=analysis.lightcurve) \
                                      .exclude(pk=pk) \
                                      .first()

    template_args = {
        'analysis': analysis.get_summary_obj(),
        'lightcurve': analysis.lightcurve,
        'image_filters': ImageFilter.objects.all(),
        'next_image': next_image,
    }
    if hasattr(analysis, 'reduction') and analysis.reduction:
        template_args.update({
            'reduction': analysis.reduction.get_summary_obj(),
        })
        return render_to_response('reduction.html', template_args,
                context_instance=RequestContext(request))
    else:
        template_args.update({
            'no_reduction': True
        })
        return render_to_response('reduction.html', template_args,
                context_instance=RequestContext(request))

def select_target_modal(request, pk):
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        return render_to_response('submission_pending.html', {},
                context_instance=RequestContext(request))

    all_analyses = list(ImageAnalysis.objects \
            .filter(lightcurve=analysis.lightcurve) \
            .order_by('image_datetime'))

    # Pick the analyses that need targets.
    some_analyses = list(ImageAnalysis.objects \
            .filter(lightcurve=analysis.lightcurve, target_id=None) \
            .order_by('image_datetime'))

    # Find this analysis in both lists.
    next_analysis = None
    next_analysis_without_target = None
    prev_analysis = None
    all_idx = None
    some_idx = None
    try:
        all_idx = all_analyses.index(analysis)
        if all_idx < len(all_analyses) - 1:
            next_analysis = all_analyses[all_idx + 1]
        if all_idx > 0:
            prev_analysis = all_analyses[all_idx - 1]
    except ValueError:
        pass

    try:
        some_idx = some_analyses.index(analysis)
        if some_idx < len(some_analyses) - 1:
            next_analysis_without_target = some_analyses[some_idx + 1]
    except ValueError:
        pass

    template_args = {
        'analysis': analysis.get_summary_obj(),
        'next_analysis_idx': all_idx,
        'next_analysis': next_analysis,
        'prev_analysis': prev_analysis,
        'next_analysis_without_target_idx': some_idx,
        'next_analysis_without_target': next_analysis_without_target,
    }
    return render_to_response('select_target.html', template_args,
            context_instance=RequestContext(request))

def api_get_analysis_results(request, subid):
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    return JsonResponse({
        'success': True,
        'analysis': analysis.get_summary_obj(),
    })

def notes(request, pk):
    # TODO(ian): Verify owner of reduction for all these ImageAnalysis fetches.
    analysis = get_object_or_404(ImageAnalysis, pk=pk, user=request.user.id)
    analysis.notes = request.POST.get('val')
    analysis.save()
    return JsonResponse({
        'success': True,
    })
