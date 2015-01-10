import urllib2, json

def get_client_ip(request):
    """Returns the ip-address of the request"""

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def ip_to_location(ip_address, default=False):
    """Returns a tuple representing longitude, latitude of the ip address
        uses external api

        If an error occurs, use default longitude, latitude"""
    try:
        query_url = "http://api.hostip.info/get_json.php?position=true&ip=%(ip_address)s"
        #response = urllib2.urlopen(query_url % {'ip_address': ip_address})
        #data = json.loads(response.read())
        data = {}
        if 'lng' and 'lat' in data:
            return (data['lng'], data['lat'])
        else:
            return (14.6476,121.0512)

    except Exception, e:
        import logging
        logging.exception(e)

        return None if not default else (14.6476,121.0512)
