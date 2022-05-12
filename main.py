from celery.bin import celery
from flask import Flask
from celery import Celery


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app():
    flask_app = Flask(__name__)
    flask_app.config.update(
        CELERY_BROKER_URL='redis://localhost:6379',
        CELERY_RESULT_BACKEND='redis://localhost:6379'
    )

    return flask_app


app = create_app()
celery = make_celery(app)


@celery.task
def add_together(a, b):
    result = a + b
    print(result)
    return result


@app.get('/')
def index():
    return "Hello Flask & Celery!"


@app.get('/add')
def run_job():
    number = add_together.delay(4, 4)
    print(number)
    return "OK"


if __name__ == '__main__':
    app.run()
