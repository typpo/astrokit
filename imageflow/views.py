import time

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

import imageflow.s3_util as s3_util
from astrometry.util import process_astrometry_online

from astrometry.models import AstrometrySubmission, AstrometrySubmissionJob
from imageflow.models import AnalysisResult

def index(request):
    return render_to_response('index.html')

def upload_image(request):
    if request.method == 'POST':
        submissions = []
        for i in range(1, 11):
            key = 'image%d' % i
            if key not in request.FILES:
               break

            img = request.FILES[key]
            # Data is read just once to avoid rewinding.
            img_data = img.read()
            url = s3_util.upload_to_s3(img_data, 'raw', img.name)
            submissions.append(process_astrometry_online(url))

        # Redirect to submission viewing page.
        return redirect('view_submission', subid=submissions[0].subid)

    return render_to_response('upload_image.html', {},
            context_instance=RequestContext(request))

def view_submission(request, subid):
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
    }
    return render_to_response('submission.html', template_args,
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
