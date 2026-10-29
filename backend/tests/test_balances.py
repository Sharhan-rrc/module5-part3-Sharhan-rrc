import pytest
from werkzeug.security import check_password_hash
import app as app_module
def register_login(client):
    data={'first_name':'Sharhan','last_name':'Kaji','email':'sharhan@example.test','password':'test-only-password'}
    response=client.post('/api/register',data=data,follow_redirects=True)
    assert response.status_code==200 and b'Registration successful' in response.data
    user=app_module.mongo.db.users.find_one({'email':data['email']})
    assert user is not None and check_password_hash(user['password_hash'],data['password'])
    response=client.post('/api/login',data={'email':data['email'],'password':data['password']},follow_redirects=True)
    assert response.status_code==200 and b'Dashboard' in response.data
    return user['_id']
def test_decimal_deposit_withdrawal_and_balance(client):
    uid=register_login(client)
    assert b'Deposit successful' in client.post('/api/deposit',data={'amount':'600.45'},follow_redirects=True).data
    assert b'Withdrawal successful' in client.post('/api/withdraw',data={'amount':'100.20'},follow_redirects=True).data
    user=app_module.mongo.db.users.find_one({'_id':uid})
    assert user['balance']==pytest.approx(500.25)
    assert [t['type'] for t in user['transactions']]==['deposit','withdrawal']
    assert all('date' in t for t in user['transactions'])
@pytest.mark.parametrize('amount',['not-a-number','-1','0'])
def test_invalid_deposit_preserves_balance(client,amount):
    uid=register_login(client);client.post('/api/deposit',data={'amount':amount})
    assert app_module.mongo.db.users.find_one({'_id':uid})['balance']==0
def test_insufficient_funds_does_not_mutate_account(client):
    uid=register_login(client)
    r=client.post('/api/withdraw',data={'amount':'1.25'},follow_redirects=True)
    assert b'Insufficient funds' in r.data
    assert app_module.mongo.db.users.find_one({'_id':uid})['transactions']==[]
def test_session_identity_requires_valid_login(client):
    assert client.get('/api/session-user').status_code==401
    uid=register_login(client);r=client.get('/api/session-user')
    assert r.status_code==204 and r.headers['X-User-ID']==str(uid)
    client.get('/api/logout');assert client.get('/api/session-user').status_code==401
