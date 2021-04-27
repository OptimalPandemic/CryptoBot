import os.path
import asyncio
from threading import Thread
from signal import signal, SIGINT
import argparse
import logging
import yaml
import json
from six.moves.urllib.request import urlopen
from functools import wraps
from sanic import Sanic
from sanic.response import json
from jose import jwt
from trader.trader import Trader

logging.basicConfig(level=logging.ERROR)
logging.info('Starting up.....')
parser = argparse.ArgumentParser()
parser.add_argument('--config', default='config.yml', help='YAML file for configuration information')
args = parser.parse_args()
with open(args.config) as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

trader = Trader(config)
app = Sanic(name='CryptoBot')
print(trader.balance)

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

@app.get('/')
async def get(self):
    return json({})

@app.get('/state')
async def get(self):
    data = trader.state
    return json(data)

@app.get('/orders')
async def orders(self):
    data = trader.orders
    return json(data)

@app.get('/balance')
async def balance(self):
    data = trader.balance
    return json(data)

@app.post('/start')
async def start(self):
    trader.shouldRun(True)
    return json({})

@app.post('/stop')
async def stop(self):
    trader.shouldRun(False)
    return json({})

@app.post('/params')
async def params(self):
    params = {}
    request_data = self.request.body
    if 'symbol' in request_data:
        params['symbol'] = request_data['symbol']
    if 'target' in request_data:
        params['target'] = request_data['target']
    if 'grid_size' in request_data:
        params['grid_size'] = request_data['grid_size']
    if 'limit' in args:
        params['limit'] = request_data['limit']
    trader.params(params)
    return json(params)

def async_action(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return decorated

async def get_token_auth_header():
    # Obtains the access token from the Authorization Header
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)
    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen("https://"+config['auth0_domain']+"/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}

        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }

        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=['RS256'],
                    audience=config['auth0_backend_audience'],
                    issuer="https://"+config['auth0_domain']+"/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    "please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 400)

            _app_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 400)
    return decorated


def main():
    trader.start()
    logging.info(f'Starting web server....')
    loop = asyncio.get_event_loop()
    server = app.create_server(host="0.0.0.0", port=config['backend_port'], return_asyncio_server=True)
    task = asyncio.ensure_future(server)
    loop.run_forever()
    

if __name__ == "__main__":
    main()