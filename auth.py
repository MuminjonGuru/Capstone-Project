from flask import request, _request_ctx_stack
from jose import jwt
import json
from functools import wraps
from config import auth0_config
from urllib.request import urlopen

#============================================================#
# Auth0 Config
#============================================================#

AUTH0_DOMAIN = auth0_config['AUTH0_DOMAIN']
ALGORITHMS   = auth0_config['ALGORITHMS']
API_AUDIENCE = auth0_config['API_AUDIENCE']

#============================================================#
# AuthError
#============================================================#

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

#============================================================#
# Auth Functions
#============================================================#        

def get_token_auth_header():
    auth = request.headers.get('Authorization', None)

    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    
    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    
    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    return parts[1]

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'Invalid',
            'description': 'Permissions not include in JWT'
        }, 400)

    if 'permission' not in payload['permissions']:
        raise AuthError({
            'code': 'Unauthorized',
            'description': 'Permission not found'
        }, 403)

    return True

def verify_decode_jwt(token):
    # Token verification
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    
    # Check if Key id is in unverified header
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'Invalid_header',
            'description': 'Authorization Invalid.'
        }, 401)

    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:           
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload

        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)    

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token Expired'
            }, 401)

    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

# decorater method
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                raise AuthError({
                    'code': 'Unauthorized',
                    'description': 'Permissions not found'
                }, 401)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator            