import logging
from datetime import timedelta

from astropy.time import Time
import callhorizons

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_lighttime_correction(analysis):
    q = callhorizons.query(analysis.lightcurve.target_name)
    jd = Time(analysis.image_datetime).jd
    q.set_discreteepochs(jd)
    # TODO(ian): Allow user to set observatory code, or choose the one closest
    # to them.  https://www.minorplanetcenter.net/iau/lists/ObsCodesF.html
    # Currently defaulting to Greenwich.
    q.get_ephemerides(0)
    if 'lighttime' not in q.fields:
        logger.warn('Could not look up lighttime for target %s. Got %s' % \
                    (analysis.lightcurve.target_name, q.fields))
        return None

    sec = q['lighttime'][0]
    adjusted_dt = analysis.image_datetime - timedelta(seconds=sec)
    ret = Time(adjusted_dt).jd
    logger.info('Applied lighttime correction of %f sec to target %s: %f -> %f' % \
                (sec, analysis.lightcurve.target_name, jd, ret))
    return ret

def get_jd_for_analysis(analysis):
    if analysis.image_jd_corrected:
        return analysis.image_jd_corrected
    return Time(analysis.image_datetime).jd
