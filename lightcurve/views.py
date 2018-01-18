from django.http import JsonResponse
from django.shortcuts import render

def edit_lightcurve(request):
    return JsonResponse({
        'success': True,
        'msg': 'Your upload was successful, but light curve page not yet implemented!',
    })
