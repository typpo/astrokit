from django.http import JsonResponse
from django.shortcuts import render

def edit_lightcurve(request, lightcurve_id):
    return JsonResponse({
        'success': True,
        'msg': 'Your upload was successful, but light curve page not yet implemented!',
    })
