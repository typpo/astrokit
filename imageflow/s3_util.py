import boto
from boto.s3.key import Key

def upload_to_s3(name, key_prefix, img_data):
    '''
    Upload an image to s3 and return the url to it.
    '''
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME,
            validate=True)
    k = Key(bucket)
    k.key = '%s/%d-%s' % (key_prefix, int(time.time()), name)

    k.set_metadata('Content-Type', _guess_mime_type(name))
    k.set_contents_from_string(img_data)
    k.set_acl('public-read')
    return k.generate_url(expires_in=0, query_auth=False)

def _guess_mime_type(filename):
    # TODO(ian): More mime types.
    if filename.endswith('fits'):
        return 'image/fits'
    return 'image/jpeg'
