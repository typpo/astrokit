import os

AWS_ACCESS_KEY_ID = os.environ.get('ASTROKIT_AWS_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('ASTROKIT_AWS_SECRET')
AWS_STORAGE_BUCKET_NAME = 'astrokit-uploads'

# The region of your bucket, more info:
# http://docs.aws.amazon.com/general/latest/gr/rande.html#s3_region
S3DIRECT_REGION = 'us-east-1'

# Destinations in the following format:
# {destination_key: (path_or_function, auth_test, [allowed_mime_types], permissions, custom_bucket)}
#
# 'destination_key' is the key to use for the 'dest' attribute on your widget or model field
S3DIRECT_DESTINATIONS = {
    # Allow anybody to upload jpegs and pngs.
    # TODO cache-control
    'imgs': ('imageflow/images', lambda u: True, ['image/jpeg', 'image/png'],),
}
