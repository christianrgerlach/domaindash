import socket
import ssl
import datetime
import logging

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




