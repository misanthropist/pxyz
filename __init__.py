import click
from flask import Flask
from pxyz.settings import config
from pxyz.extensions import db
from pxyz.models import Item, User
from pxyz.blueprints.itempad import itempad_bp
from pxyz.blueprints.upload import upload_bp
from pxyz.blueprints.message import message_bp
from pxyz.blueprints.user import user_bp
from pxyz.util import forge

def create_app(config_name):
    app = Flask('pxyz')
    app.config.from_object(config[config_name])
    register_extensions(app)
    register_blueprints(app)
    register_shell_context(app)
    register_commands(app)
    return app

def register_extensions(app):
    db.init_app(app)

def register_blueprints(app):
    app.register_blueprint(itempad_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(user_bp)

def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, Item=Item, User=User)

def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        if drop:
            click.echo('drop tables')
            db.drop_all()

            click.echo('processing ' + app.config['PXYZ_UPLOAD_PATH'])
            click.echo('initialized database')
            db.create_all()
            
            forge.gen_all(app)
            db.session.commit()

if __name__ == "__main__":
    pass