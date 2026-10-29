const {test}=require('node:test');
const assert=require('node:assert/strict');
const {createApp,groupTransactions}=require('../app');
test('monthly reports preserve amounts and sort newest month first',()=>{
 const groups=groupTransactions([{date:'2026-09-10T10:00:00Z',amount:10.25,type:'deposit'},{date:'2026-10-01T10:00:00Z',amount:600.45,type:'deposit'},{date:'2026-10-02T10:00:00Z',amount:100.20,type:'withdrawal'}]);
 assert.equal(groups.length,2); assert.equal(groups[0].month,'October 2026');
 assert.equal(groups[0].transactions.length,2); assert.equal(groups[0].transactions[1].amount,100.20);
});
test('unauthenticated reports do not read user data',async()=>{
 const app=createApp({collection(){throw new Error('must not read database');}});
 const server=app.listen(0,'127.0.0.1');
 await new Promise((resolve,reject)=>{server.once('listening',resolve);server.once('error',reject);});
 try {const r=await fetch(`http://127.0.0.1:${server.address().port}/api/transactions`); assert.equal(r.status,401);}
 finally {server.close();}
});
test('verified identity restricts report to that account',async()=>{
 const id='507f1f77bcf86cd799439011'; let queried;
 const app=createApp({collection(){return {async findOne(query){queried=query._id.toString();return {transactions:[]};}};}});
 const server=app.listen(0,'127.0.0.1');
 await new Promise((resolve,reject)=>{server.once('listening',resolve);server.once('error',reject);});
 try {const r=await fetch(`http://127.0.0.1:${server.address().port}/api/transactions`,{headers:{'X-User-ID':id}}); assert.equal(r.status,200);assert.equal(queried,id);assert.deepEqual(await r.json(),[]);}
 finally {server.close();}
});
