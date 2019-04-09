import requests
import base64
from requests.auth import HTTPBasicAuth
import json


oktaInstance = "yourOktaInstanceUrl"
client_id = "yourId"
client_secret = "yourSecret"
tokenEndpoint = oktaInstance + "/oauth2/anzSvrIdentifier/v1/token"
redirUri = "http://localhost:8000"
scope = "customScope"
response_type = "code"

testEndpointUrl = "http://ip_of_endpoint:8081/boo"


def getAznCode():
	heads = {'accept': 'application/json',
			  'cache-control': 'no-cache',
			  'content-type': 'application/x-www-form-urlencoded'}
	params = {'grant_type': 'client_credentials',
				'scope': scope}
	response = requests.post(tokenEndpoint, auth=HTTPBasicAuth(client_id,client_secret), data=params)
	if (response.status_code != 200):
		print("Azn request failed. Error code: ", response.status_code)
		print("The errors tend to be in the body of the response:", response.content)
	else:	
		#print("url: ", response.content)
		jsonResponse = response.json()
		try:
			print("token: ", jsonResponse.get('access_token'))
			return jsonResponse.get('access_token')
			# NOTE: there is an expires_in value which has a value set in seconds.
		except ValueError:
			return "Catch this. One day"

def makeTestCall(azncode):
   heads = {'Authorization': azncode,
   			'accept': 'application/json',
			'content-type': 'application/x-www-form-urlencoded'}
   result = requests.get(testEndpointUrl, headers=heads)
   print("result: ", result.content)



def main():
	aznCode = getAznCode()
	makeTestCall(aznCode)



if __name__=='__main__': main()
