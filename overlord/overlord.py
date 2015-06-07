from celery import Celery

app = Celery(
  'overlord',
  broker='amqp://guest:guest@localhost//',
  backend='amqp',
  include=["backup", "server", "static"],
)
app.config_from_object('celeryconfig')

if __name__ == '__main__':
  app.start()
