var celery = require('node-celery');
var client = celery.createClient({
  CELERY_BROKER_URL: 'amqp://guest:guest@localhost',
  CELERY_RESULT_BACKEND: 'amqp'
});
var triggerBuild = client.createTask('overlord.triggerBuild');
var backupMySQLWithHost = client.createTask('overlord.backupMySQLWithHost');

client.on('error', function(err) {
    console.log(err);
});

client.on('connect', function() {
  /*var result = triggerBuild.call(["intranet", "master"]);
  result.on('ready', function(message) {
      console.log(message);
      client.end();
      client.broker.destroy();
  });*/
  var result = backupMySQLWithHost.call([]);
  result.on('ready', function(message) {
      console.log(message);
      client.end();
      client.broker.destroy();
  });
});