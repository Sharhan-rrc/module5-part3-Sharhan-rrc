const express = require('express');
const { MongoClient, ObjectId } = require('mongodb');
function groupTransactions(transactions) {
  const groups = new Map();
  for (const tx of transactions || []) {
    const date = new Date(tx.date);
    if (!Number.isFinite(date.getTime())) continue;
    const key = date.toISOString().slice(0, 7);
    if (!groups.has(key)) groups.set(key, {month: date.toLocaleString('en-CA', {month:'long', year:'numeric', timeZone:'UTC'}), transactions: []});
    groups.get(key).transactions.push({type:tx.type, amount:tx.amount, date:date.toISOString()});
  }
  return [...groups.entries()].sort((a,b)=>b[0].localeCompare(a[0])).map(([,value])=>value);
}
function createApp(db) {
  const app = express();
  app.get('/health', async (req,res) => {
    try { await db.command({ping:1}); res.json({status:'healthy', service:'transactions'}); }
    catch { res.status(503).json({status:'unavailable'}); }
  });
  // NGINX overwrites X-User-ID after validating the Flask login session.
  // No host port is published for this service.
  app.get(['/api/transactions','/api/transactions/'], async (req,res) => {
    const id = req.get('X-User-ID');
    if (!id || !ObjectId.isValid(id)) return res.status(401).json({error:'Not logged in'});
    try {
      const user = await db.collection('users').findOne({_id:new ObjectId(id)});
      if (!user) return res.status(404).json({error:'User not found'});
      res.set('X-YMB-Service','transactions').json(groupTransactions(user.transactions));
    } catch { res.status(500).json({error:'Unable to load transactions'}); }
  });
  return app;
}
if (require.main === module) {
  const client = new MongoClient(process.env.MONGO_URI || 'mongodb://mongo:27017/bank_app');
  client.connect().then(async () => {
    const db=client.db('bank_app'); await db.command({ping:1});
    const server=createApp(db).listen(process.env.PORT || 3000, '0.0.0.0', () => console.log('Yarrow-Mullein Bank Services: transactions ready'));
    process.on('SIGTERM',()=>server.close(async()=>{await client.close();process.exit(0);}));
  }).catch(err=>{console.error('MongoDB connection failed:',err.message);process.exit(1);});
}
module.exports={createApp,groupTransactions};
