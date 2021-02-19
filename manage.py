import app
from app import app as pxyz

import click

@pxyz.cli.command()
def hello():
    click.echo(2+1)

import os,json
@pxyz.cli.command()
def mztdb():
    with open(os.path.join('app','static','mzt','data.json'), 'r') as f:
        data = json.load(f)
    for tag, content in data.items():
        for k, v in content.items():
            for title, urls in v.items():
                item = app.models.Item(
                    title=title,
                    url="mzt/data.json?{}".format(k),
                    logo='../mzt/pics/'+urls[0].split('/')[-1],
                    score=0,
                    info="mzt"
                )
                app.db.session.add(item)
        app.db.session.commit()

@pxyz.cli.command()
def epubdb():
    with open(os.path.join('app', 'static', 'book', 'epub_meta.json'), 'r') as f:
        data = json.load(f)
    # for key in os.listdir(os.path.join("app", 'static', 'book', 'books')):
    #     print(len(data.keys()))
    #     if key not in data.keys():
    #         print(key)

    for key in data.keys():
        item = app.models.Item(
            title=key,
            url="book/books/{}".format(key),
            info='book'
        )
        app.db.session.add(item)
    app.db.session.commit()


if __name__ == '__main__':
    app.app.run()