""" Import required libraries """
import json
import requests
import sys, os, base64, datetime, hashlib, hmac 


def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning



def main(access_key, secret_key, region, domain_to_check):
    """ Get domain name availability """

    method = 'POST'
    service = 'route53domains'
    host = 'route53domains.'+ region +'.amazonaws.com'
    endpoint = 'https://route53domains.'+ region + '.amazonaws.com'
    data = {
        "DomainName": domain_to_check
    }
    json_data = json.dumps(data)
    user_agent = 'Supercode Internal Testing 1.0'
    target = 'Route53Domains_v20140515.CheckDomainAvailability'
    content_type = 'application/x-amz-json-1.1'
    algorithm = 'AWS4-HMAC-SHA256'

    t = datetime.datetime.utcnow()
    amzdate = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope

    response = {
        'success': False,
        'domain name': domain_to_check,
        'available': False,
        'price': 0.0
    }

    canonical_uri = '/'
    
    canonical_headers = 'content-length:' + str(len(json_data)) + '\n' + 'content-type:' + content_type + '\n' + 'host:' + host + '\n' + 'user-agent:' + user_agent + '\n' + 'x-amz-date:' + amzdate + '\n' + 'x-amz-target:' + target + '\n'

    signed_headers = 'content-length;content-type;host;user-agent;x-amz-date;x-amz-target'

    payload_hash = hashlib.sha256(json_data).hexdigest()

    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash

    credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'
    string_to_sign = algorithm + '\n' +  amzdate + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request).hexdigest()

    signing_key = getSignatureKey(secret_key, datestamp, region, service)

    signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()

    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

    headers = { 'x-amz-date':amzdate,
                'authorization':authorization_header,
                'x-amz-target': target,
                'user-agent': user_agent,
                'content-type': content_type,
                'content-length': len(json_data),
                'connections:':'Keep-Alive'
           }

    try:
        result = requests.post(endpoint, headers=headers, data=json_data)

        status_code = result.status_code

        result = json.loads(result.text)

        if status_code == 200:
            if "error" in result:
                response["success"] = False
            else:
                response["success"] = True
                
                if result["Availability"].startswith("AVAIL"):
                    response['available'] = True
                else:
                    response['available'] = False

        else:
            response["success"] = False
    except Exception:
        response["success"] = False

    return response

