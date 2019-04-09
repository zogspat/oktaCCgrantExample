command line client:

- requires Azn server config - creation of custom scope, and access policy for it.
- requires client application config.
- sets the access token as an Authorization header.
- success = return of the json contents of the access token

server:
- Connects to the well known config, and retrieves the jwks_uri
- from there, grabs the exponent and modulus; constructs a pem version of the public key
- starts the flask server
- reads the value of the authorization header which the client sets for the /boo path.
- validates the token with the public key. If valid, returns the json value of the token
