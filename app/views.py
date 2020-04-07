import codecs
import json
from pathlib import Path

from cylleneus import __version__, settings
from cylleneus.corpus import Corpus, Work
from cylleneus.search import Collection, Searcher
from flask import render_template, request, session

from .db import Search, SearchResult, db
from .display import as_html
from .server import app

_corpora = []
for path in Path(settings.CORPUS_DIR).glob('*/*'):
    if path.is_dir() and Path(path / 'index').exists():
        _corpora.append(path.name)

_collection = None
_collection_name = None


def parse_collection(collection):
    works = []
    docs = json.loads(collection)
    for doc in docs:
        corpus, nn = doc.split(',')
        c = Corpus(corpus)
        for n in nn.strip('[]').split(', '):
            w = c.work_by_docix(int(n))
            works.append(w)
    return Collection(works=works)


def import_text(corpus, author, title, filename, content):
    kwargs = {
        'corpus':   corpus,
        'author':   author,
        'title':    title,
        'filename': filename,
    }

    try:
        c = Corpus(corpus)
        w = Work(c, author=author, title=title)
        ndocs = c.doc_count_all
        w.indexer.from_string(content=content, **kwargs)

        if c.doc_count_all > ndocs:
            success = True
        else:
            success = False
    except Exception as e:
        success = False
    return success


# TODO: add pagination
def search_request(collection, query):
    c = Collection(works=collection)

    search = Searcher(c).search(query)

    if search.results:
        return search


@app.route('/', methods=['GET', 'POST'])
def index():
    global _collection, _collection_name
    session.permanent = True

    form = request.form

    collection = form.get('collection', None)
    if collection is not None:
        session["collection"] = collection
    else:
        collection = session.get("collection", None)
    _collection = parse_collection(collection) if collection else None

    name = form.get('collection-name', None)
    if name is not None:
        session["collection-name"] = name
    else:
        if collection == "[]":
            name = session.get("collection-name", None)
    _collection_name = name if name else None
    if _collection_name:
        _collection.save(name)

    db.connect()
    history = []
    for h in Search.select():
        history.append(h)
    db.close()

    response = {
        'version':    __version__,
        'corpora':    _corpora,
        'works':      _collection.works if _collection else [],
        'collection': collection,
        'history':    history
    }
    return render_template('index.html', **response)


@app.route('/collection/select', methods=['GET'])
def collection_select():
    response = {
        'corpora': [Corpus(corpus) for corpus in _corpora]
    }
    return render_template('collection_select.html', **response)


@app.route('/collection/load', methods=['GET'])
def collection_load():
    file = Path(".collections")
    if file.exists():
        with codecs.open(file, "r", "utf8") as fp:
            _collections = json.load(fp)
    else:
        _collections = {}
    collections = []
    for name in _collections:
        collection = Collection()
        collection.load(name)
        collections.append(collection)
    response = {
        'collections': collections
    }
    return render_template('collection_load.html', **response)


@app.route('/collection/save', methods=['GET'])
def collection_save():
    global _collection

    response = {
        'collection': _collection
    }
    return render_template('collection_save.html', **response)


@app.route('/import', methods=['POST', 'GET'])
def _import():
    form = request.form

    corpus = form.get('corpus', None)
    author = form.get('author', None)
    title = form.get('title', None)
    filename = form.get('filename', None)
    content = form.get('content', None)

    if filename is not None and content is not None:
        success = import_text(corpus, author, title, filename, content)
    else:
        success = False

    response = {
        'filename': filename if filename else "Choose file...",
        'corpus':   corpus if corpus else "",
        'author':   author if author else "",
        'title':    title if title else "",
        'content':  content if content else "",
        'success':  success
    }
    return render_template('import.html', **response)


@app.route('/history', methods=['GET'])
def history():
    db.connect()
    history = []
    for h in Search.select():
        history.append(h)
    db.close()

    kwargs = request.args
    id = kwargs.get('id')
    db.connect()
    s = Search.get_by_id(id)
    db.close()

    works = []
    ids = json.loads(s.collection)
    for id in ids:
        corpus, n = id.split(',')
        c = Corpus(corpus)
        w = c.work_by_docix(int(n))
        works.append(w)

    results = [r.html for r in SearchResult.select().where(SearchResult.search == s)]

    response = {
        'version':    __version__,
        'collection': s.collection,
        'works':      works,
        'corpora':    _corpora,
        'query':      s.query,
        'history':    history,
        'results':    results,
        'count':      len(s.results),
    }
    return render_template('index.html', **response)


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        form = request.form
    else:
        form = request.args

    collection = form.get('collection')
    query = form.get('query')

    works = []

    ids = json.loads(collection)
    for id in ids:
        corpus, n = id.split(',')
        c = Corpus(corpus)
        if not c.is_searchable:
            c.download()
        w = c.work_by_docix(int(n))
        works.append(w)

    results = search_request(works, query)

    if results:
        db.connect()
        try:
            s = Search.get(query=query, collection=collection),
        except Search.DoesNotExist:
            names = [f"{work.author}, {work.title}" for work in works]
            s = Search.create(
                query=query,
                collection=collection,
                prettified=f"{'; '.join(names)}",
                minscore=results.minscore,
                top=results.top,
                start_time=results.start_time,
                end_time=results.end_time,
                maxchars=results.maxchars,
                surround=results.surround
            )
            s.save()
        finally:
            for href in results.highlights:
                r = SearchResult.get_or_create(
                    search=s,
                    html=next(as_html([href, ]))
                )
                if r[1]:
                    r[0].save()
        db.close()

    db.connect()
    history = []
    for h in Search.select():
        history.append(h)
    db.close()

    response = {
        'version':    __version__,
        'collection': collection,
        'works':      works,
        'corpora':    _corpora,
        'query':      query,
        'history':    history,
        'results':    as_html(results.highlights) if results else [],
        'count':      results.count if results else (0, 0),
    }
    return render_template('index.html', **response)

