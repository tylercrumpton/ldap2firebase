"""Super-simple HTTP API for creating a Firebase Auth Token from an LDAP login.

Run with something like:
    gunicorn --bind 127.0.0.1:8000 ldap2firebase

If the LDAP server is not localhost:389, specify a server with the LDAP_SERVER env variable.
Make sure to have a servicekey.json file from Firebase in the same directory as ldap2firebase.py.
NOTE: You should always run this behind a TLS-secured HTTP proxy because LDAP credentials are passed around.
"""
import os
import firebase_admin
from firebase_admin import auth
import ldap3
from flask import Flask, request

cred = firebase_admin.credentials.Certificate('./servicekey.json')
firebase_app = firebase_admin.initialize_app(cred)

application = Flask(__name__)

@application.route("/auth", methods=['POST'])
def ldap_firebase_auth():
    """Example call:
        curl -X POST http://localhost:8000/auth -d 'username=some_user&password=their_password'
    """
    ldap_server = ldap3.Server(os.environ.get('LDAP_SERVER', 'localhost'))

    uid = request.form['username']
    password = request.form['password']

    try:
        ad = ldap3.Connection(
            ldap_server,
            "uid={user},ou=people,dc=makerslocal,dc=org".format(user=uid),
            password,
            auto_bind=ldap3.AUTO_BIND_NO_TLS,
            pool_lifetime=300
        )
        if ad.result['result'] != 0:
            raise ldap3.core.exceptions.LDAPBindError
    except ldap3.core.exceptions.LDAPBindError:
        return "NO", 401

    ad.search(
        search_base="ou=groups,dc=makerslocal,dc=org",
        search_filter="(uniqueMember=uid={user},ou=people,dc=makerslocal,dc=org)".format(user=uid),
        attributes=["cn"]
    )
    additional_claims = {"groups": [group_entry['cn'][0] for group_entry in ad.entries]}

    is_maker = ad.search(
        search_base="ou=people,dc=makerslocal,dc=org",
        search_filter="(&(uid={user})(objectClass=Maker))".format(user=uid),
    )
    if is_maker:
        additional_claims["groups"].append("maker")

    custom_token = auth.create_custom_token(uid, additional_claims)
    return custom_token