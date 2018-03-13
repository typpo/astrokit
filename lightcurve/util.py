from django.db.models import Case, Value, When, IntegerField

def ordered_analysis_status():
    return Case(
        When(analysis__status='ASTROMETRY_PENDING', then=Value(0)),
        When(analysis__status='PHOTOMETRY_PENDING', then=Value(1)),
        When(analysis__status='REVIEW_PENDING', then=Value(2)),
        When(analysis__status='REDUCTION_COMPLETE', then=Value(3)),
        When(analysis__status='ADDED_TO_LIGHT_CURVE', then=Value(4)),
        When(analysis__status='FAILED', then=Value(5)),
        output_field=IntegerField(), )