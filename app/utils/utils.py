import socket
import ssl
import datetime
import logging
import requests
import json

mxtoolbox_api_key = 'd31bcf1f-e2d4-44ff-b13c-4a446318fe20'

mxtoolbox_request_header = {'Authorization': mxtoolbox_api_key}

def get_mxtoolbox_response(hostname):

    response = requests.get('https://api.mxtoolbox.com/api/v1/lookup/mx/' + hostname, headers = mxtoolbox_request_header)

    if response.status_code == 200:
        return json.loads(response.content)
    else:
        return None

def ssl_expiry_datetime(hostname):
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'

    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=hostname,
    )
    # 3 second timeout because Lambda has runtime limitations
    conn.settimeout(3.0)

    conn.connect((hostname, 443))
    ssl_info = conn.getpeercert()
    # parse the string from the certificate into a Python datetime object
    return datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)

def ssl_valid_time_remaining(hostname):
    """Get the number of days left in a cert's lifetime."""
    expires = ssl_expiry_datetime(hostname)
    logging.debug(
     "SSL cert for %s expires at %s",
     hostname, expires.isoformat()
    )
    return expires - datetime.datetime.utcnow()

def ssl_expires_in(hostname, buffer_days=14):
    """Check if `hostname` SSL cert expires is within `buffer_days`.

    Raises `AlreadyExpired` if the cert is past due
    """
    remaining = ssl_valid_time_remaining(hostname)

    # if the cert expires in less than two weeks, we should reissue it
    if remaining < datetime.timedelta(days=0):
        # cert has already expired - uhoh!
        raise AlreadyExpired("Cert expired %s days ago" % remaining.days)
    elif remaining < datetime.timedelta(days=buffer_days):
        # expires sooner than the buffer
        return True
    else:
        # everything is fine
        return False




