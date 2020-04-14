==============================
Cylleneus web search interface
==============================

.. image:: https://img.shields.io/badge/cylleneus-next--gen%20corpus%20search%20for%20ancient%20languages-blue.svg
        :target: https://github.com/wmshort/cylleneus

.. image:: https://travis-ci.org/cylleneus/web-ui.svg?branch=master
    :target: https://travis-ci.org/cylleneus/web-ui

* Free software: Apache Software License 2.0
* Documentation: https://cylleneus.readthedocs.io.


Overview
--------

Cylleneus is a next-generation search engine for electronic corpora of Greek and Latin, which enables texts to be searched on the basis of their semantic and morpho-syntactic properties. This means that, for the first time, texts can be searched by the *meanings* of words as well as by the kinds of grammatical constructions they occur in. Semantic search takes advantage of the `Ancient Greek WordNet <https://greekwordnet.chs.harvard.edu/>`_ and `Latin WordNet <https://latinwordnet.exeter.ac.uk/>`_ and is fully implemented, and thus is available for any annotated or plain-text corpus. However, semantic queries may still be imprecise due to the on-going nature of these two projects. Syntactic search functionality is still under development and is available for only certain structured corpora.  Morphological searching and query filtering will work with any Latin corpus, and any Greek corpus with sufficient morhological annotation.


Installation
------------

Clone this repository and then ``$ python setup.py install``.


Searching
---------

Run ``$ cylleneus-web``.

Then point your browser at ``http://127.0.0.1:5000``. The web app can accommodate the full range of query types, and has functionality for viewing available corpora, importing new plain-text files, and exporting search results.


Credits
-------

© 2019 William Michael Short.
