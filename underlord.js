var celery = require('node-celery');
var client = celery.createClient({
  CELERY_BROKER_URL: 'amqp://guest:guest@localhost',
  CELERY_RESULT_BACKEND: 'amqp'
});
var triggerBuild = client.createTask('overlord.triggerBuild');
var backupMySQLWithHost = client.createTask('overlord.backupMySQLWithHost');
var backupMongo = client.createTask('overlord.backupMongo');
var backupMySQLWithoutHost = client.createTask('overlord.backupMySQLWithoutHost');
var rebuildWikiPassword = client.createTask('overlord.rebuildWikiPassword');

client.on('error', function(err) {
    console.log(err);
});

client.on('connect', function() {
  /*
  var result = triggerBuild.call(["intranet", "master"]);
  result.on('ready', function(message) {
      console.log(message);
      client.end();
      client.broker.destroy();
  });
  */
  var result = rebuildWikiPassword.call([]);
  result.on('ready', function(message) {
      console.log(message);
      client.end();
      client.broker.destroy();
  });
  
});