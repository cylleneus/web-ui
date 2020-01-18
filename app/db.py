import peewee

from cylleneus.utils import dtformat

db = peewee.SqliteDatabase("history.db")


class Search(peewee.Model):
    """Represents a single search instance."""

    class Meta(object):
        database = db

    query = peewee.CharField()
    collection = peewee.TextField()
    prettified = peewee.TextField()
    minscore = peewee.IntegerField(null=True)
    top = peewee.IntegerField(null=True)
    start_time = peewee.DateTimeField()
    end_time = peewee.DateTimeField()
    maxchars = peewee.IntegerField(null=True)
    surround = peewee.IntegerField(null=True)

    @property
    def dt(self):
        return dtformat(self.start_time)

    def __str__(self):
        return self.query

    def __repr__(self):
        return f"Search(query={self.query}, collection={self.collection})"


Search.create_table(fail_silently=True)


class SearchResult(peewee.Model):
    class Meta(object):
        database = db

    search = peewee.ForeignKeyField(Search, related_name="results")
    html = peewee.TextField()


SearchResult.create_table(fail_silently=True)
