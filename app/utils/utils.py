import socket
import ssl
import datetime
import logging
import requests

#personal
#mxtoolbox_api_key = 'd31bcf1f-e2d4-44ff-b13c-4a446318fe20'

#itsg
mxtoolbox_api_key = 'bea9b9cc-01f7-4af9-af34-b2e99fdb7d4e'

mxtoolbox_request_header = {'Authorization': mxtoolbox_api_key}

def get_mxtoolbox_response(hostname, report):
    response = requests.get('https://api.mxtoolbox.com/api/v1/lookup/' + report + '/' + hostname, headers = mxtoolbox_request_header)
    if response.status_code == 200:
        return response.content.decode("utf-8")
    else:
        print('Error!  Return code: ' + str(response.status_code) + '\n' + str(response.content))
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
    return datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)

def ssl_valid_time_remaining(hostname):
    expires = ssl_expiry_datetime(hostname)
    logging.debug(
     "SSL cert for %s expires at %s",
     hostname, expires.isoformat()
    )
    return expires - datetime.datetime.utcnow()