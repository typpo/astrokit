from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.utils.dateparse import parse_datetime

from astrometry.util import create_new_lightcurve

from astrometry.models import AstrometrySubmission, AstrometrySubmissionJob
from imageflow.models import ImageAnalysis, ImageFilter, Reduction, UserUploadedImage

def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))

def upload_image(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            imgs = [request.FILES[key] for key in request.FILES]
            lightcurve = create_new_lightcurve(request.user, imgs)

            # Redirect to submission viewing page.
            return JsonResponse({
                'details': 'success',
                'redirect_url': reverse('edit_lightcurve', kwargs={'lightcurve_id': lightcurve.id}),
            })

        return render_to_response('upload_image.html', {},
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
        'image_filters': ImageFilter.objects.all(),
    }
    return render_to_response('summary.html', template_args,
            context_instance=RequestContext(request))

def set_datetime(request, pk):
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
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
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        return JsonResponse({
            'success': False,
            'msg': 'Astrometry is still pending',
        })

    analysis.target_id = request.POST.get('val')
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

def set_color_index_1(request, pk):
    analysis, filter_band = resolve_band(request, pk)
    analysis.get_or_create_reduction()
    analysis.reduction.color_index_1 = filter_band
    analysis.reduction.save()
    return JsonResponse({
        'success': True,
        'msg': 'Resolved input to %s' % str(filter_band)
    })

def set_color_index_2(request, pk):
    analysis, filter_band = resolve_band(request, pk)
    analysis.get_or_create_reduction()
    analysis.reduction.color_index_2 = filter_band
    analysis.reduction.save()
    return JsonResponse({
        'success': True,
        'msg': 'Resolved input to %s' % str(filter_band)
    })

def set_image_companion(request, pk):
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        return JsonResponse({
            'success': False,
            'msg': 'Astrometry is still pending',
        })
    analysis.get_or_create_reduction()

    imageid = request.POST.get('val')
    analysis.reduction.image_companion = UserUploadedImage.objects.get(pk=imageid)
    analysis.reduction.save()
    return JsonResponse({
        'success': True,
        'msg': 'Resolved input'
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

def set_second_order_extinction(request, pk):
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        return JsonResponse({
            'success': False,
            'msg': 'Astrometry is still pending',
        })
    analysis.get_or_create_reduction()
    return set_float(request, pk, 'second_order_extinction', on_reduction=True)

def set_float(request, pk, attrname, on_reduction=False):
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        return JsonResponse({
            'success': False,
            'msg': 'Astrometry is still pending',
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
    analysis = get_object_or_404(ImageAnalysis, pk=pk)

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

def set_photometry_param(request, pk):
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
        if param == 'sigma':
            params.sigma_psf = float(val)
        elif param == 'separation':
            params.crit_separation = float(val)
        elif param == 'threshold':
            params.threshold = float(val)
        elif param == 'fitshape':
            params.box_size = int(val)
        elif param == 'iters':
            params.iters = int(val)
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

def point_sources(request, pk):
    # TODO(ian): Dedup this with above code.
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    if analysis.status == ImageAnalysis.ASTROMETRY_PENDING:
        return render_to_response('submission_pending.html', {},
                context_instance=RequestContext(request))

    template_args = {
        'analysis': analysis.get_summary_obj(),
        'phot_settings': analysis.get_or_create_photometry_settings(),
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

    # Other images in this light curve.
    potential_image_companions = analysis.lightcurve.useruploadedimage_set.all()

    # Next image for user to process in this light curve.
    next_image = ImageAnalysis.objects.filter(status=ImageAnalysis.REVIEW_PENDING,
                                              useruploadedimage__lightcurve=analysis.lightcurve) \
                                      .exclude(pk=pk) \
                                      .first()

    template_args = {
        'analysis': analysis.get_summary_obj(),
        'image_filters': ImageFilter.objects.all(),

        'potential_image_companions': potential_image_companions,
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

def api_get_analysis_results(request, subid):
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    return JsonResponse({
        'success': True,
        'analysis': analysis.get_summary_obj(),
    })

def notes(request, pk):
    # TODO(ian): Verify owner of reduction for all these ImageAnalysis fetches.
    analysis = get_object_or_404(ImageAnalysis, pk=pk)
    analysis.notes = request.POST.get('val')
    analysis.save()
    return JsonResponse({
        'success': True,
    })
