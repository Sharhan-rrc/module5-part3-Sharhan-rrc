"""Exercise real services through NGINX; never substitute mocks for this check."""
import urllib.request, urllib.parse, urllib.error, http.cookiejar, json, uuid, socket
from datetime import datetime, timezone

base='http://localhost'
jar=http.cookiejar.CookieJar()
client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
def request(path,data=None):
    payload=urllib.parse.urlencode(data).encode() if data is not None else None
    return client.open(base+path,payload,timeout=20)
assert b'Sharhan Kaji' in request('/').read()
try:
    request('/api/transactions')
    raise AssertionError('Transactions must require login')
except urllib.error.HTTPError as exc:
    assert exc.code==401
email='ci-'+uuid.uuid4().hex+'@example.test'
credentials={'email':email,'password':uuid.uuid4().hex}
registration=dict(credentials,first_name='CI',last_name='Test')
assert b'Registration successful' in request('/api/register',registration).read()
assert b'Dashboard' in request('/api/login',credentials).read()
assert b'Deposit successful' in request('/api/deposit',{'amount':'600.45'}).read()
assert b'Withdrawal successful' in request('/api/withdraw',{'amount':'100.20'}).read()
assert b'$500.25' in request('/api/dashboard').read()
response=request('/api/transactions')
assert response.headers.get('X-YMB-Service')=='transactions'
groups=json.load(response)
assert sum(len(g['transactions']) for g in groups)==2
request('/api/logout').read()
try:
    request('/api/transactions')
    raise AssertionError('Logout must remove access')
except urllib.error.HTTPError as exc:
    assert exc.code==401
for port in [5000,3000,27017]:
    with socket.socket() as connection:
        connection.settimeout(1)
        assert connection.connect_ex(('127.0.0.1',port))!=0, f'Unexpected host port {port}'
print(json.dumps({'status':'passed','timestamp_utc':datetime.now(timezone.utc).isoformat(),'checks':['portfolio','registration','login','decimal deposit','decimal withdrawal','balance 500.25','authenticated JavaScript report','logout','no direct host ports']},indent=2))
