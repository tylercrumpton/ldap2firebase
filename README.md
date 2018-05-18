# ldap2firebase
Simple Example HTTP API for generating Firebase Custom Tokens using LDAP logins.

## Usage
First clone the repo, then install the requirements:

    pip install -r requirements.txt

Then, install a WSGI server like gunicorn:

    pip install gunicorn
    
Generate a `servicekey.json` file in the Firebase Console and save it to the same directory as ldap2firebase.py.

If your LDAP server is not hosted on `localhost:389`, specify a server with the LDAP_SERVER env variable:

    LDAP_SERVER=myhost.local:5555

Run the application using your WSGI server. For example, with gunicorn, run:

    gunicorn --bind 127.0.0.1:8000 ldap2firebase
    
Hit the HTTP `/auth` endpoint with a username/password and it should return a Firebase auth token if successful.
It will return a `401` if the authentication fails:

    curl -X POST http://localhost:8000/auth -d 'username=some_user&password=their_password'

## Security Note
You should always run this behind a TLS-secured HTTPS proxy because LDAP credentials are passed over plaintext. Stay safe!
