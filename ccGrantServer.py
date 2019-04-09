from flask import Flask
from flask import request
from flask import jsonify
import requests
import jwt
import six
import json
import base64
import struct
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


# this is an adapted version of https://github.com/jpf/okta-jwks-to-pem/blob/master/jwks_to_pem.py
# this was also very useful: https://robertoprevato.github.io/Validating-JWT-Bearer-tokens-from-Azure-AD-in-Python/

app = Flask(__name__)

oktaInstance = "yourInstanceUrl"
tokenEndpoint = oktaInstance + "/oauth2/aznServerIdentifier/v1/token"
# note that the reference to the well-known config is azn server specific
oidConfigUrl = oktaInstance + "/oauth2/aznServerIdentifier/.well-known/openid-configuration"
pubKeyPem = ""
# the best way to double check these is using the token preview for the azn server:
validAudiences = "api://default"
issuer =  oktaInstance + "/oauth2/aznServerIdentifier"

def validate_jwt(jwt_to_validate):
    decoded = jwt.decode(jwt_to_validate,
                         pubKeyPem,
                         verify=True,
                         algorithms=['RS256'],
                         audience=validAudiences,
                         issuer=issuer)
    # if we get here, the JWT is validated
    #return decoded
    return decoded

@app.route('/boo')
def data():
   result = validate_jwt((request.headers.get('Authorization')))
   return jsonify(result)


def intarr2long(arr):
   return int(''.join(["%02x" % byte for byte in arr]), 16)

def base64_to_long(data):
   if isinstance(data, six.text_type):
      data = data.encode("ascii")

   # urlsafe_b64decode will happily convert b64encoded data
   _d = base64.urlsafe_b64decode(bytes(data) + b'==')
   return intarr2long(struct.unpack('%sB' % len(_d), _d))

def rsa_pem_from_jwk(jsonKeyResult):
   print(jsonKeyResult['keys'][0]['n'])
   exponent = base64_to_long(jsonKeyResult['keys'][0]['e'])
   modulus = base64_to_long(jsonKeyResult['keys'][0]['n'])
   numbers = RSAPublicNumbers(exponent, modulus)
   public_key = numbers.public_key(backend=default_backend())
   pem = public_key.public_bytes(
      encoding=serialization.Encoding.PEM,
      format=serialization.PublicFormat.SubjectPublicKeyInfo
   )
   return pem

def getValidationKey():
   configResult = requests.get(oidConfigUrl)
   jsonResponse = configResult.json()
   keyDistroURL = jsonResponse.get('jwks_uri')
   keyResult = requests.get(keyDistroURL)
   jsonKeyResult = json.loads(keyResult.content)
   print(json.dumps(jsonKeyResult['keys'][0]['n']))
   n = base64.b64decode(json.dumps(jsonKeyResult['keys'][0]['n']+"=="))
   e = base64.b64decode(json.dumps(jsonKeyResult['keys'][0]['e']+"=="))
   #inner = jsonKeyResult.get('keys')[0].get('n')
   pubKeyPem = rsa_pem_from_jwk(jsonKeyResult)
   return pubKeyPem

if __name__=='__main__':
   pubKeyPem = getValidationKey()
   print(pubKeyPem)
   # not localhost!!
   app.run(host='yourIp', port=8081)
