# Manually testing of OAuth authentication using KeyCloak


There are two ways to authenticate using the oAuth endpoints. Both of them require some human assistance due to the authentication provider, keycloak, needing a web browser to log in.

## First way

The first way is to use the login endpoint with no parameters. This redirects the user to the Keycloak login page. If the user credentials are valid, the user gets automatically redirected back to the API and should receive a JWT token in the body of the response.

## Second way

The second way is meant for devices with no access to an internet browser. The client needs to use the login endpoint with an empty device parameter: /login?device.

The client then receives a URL that needs to be sent to a user who uses it to login using keycloak. During this time it is expected from the client to be polling the login endpoint to know when it gets authenticated. This is done by using the device code received from the previous request in the device parameter: /login?device=<device_code>. If the authentication is finished, the JWT token is received in the response body.
To refresh JWT tokens, the client should call the token_refresh endpoint. The refresh token itself is generated with each normal token and is then passed as a parameter to the endpoint: /token_refresh?refresh_token=<refresh_token>.