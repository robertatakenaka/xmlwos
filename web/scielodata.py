import json
import os
from tornado import (
    httpserver,
    httpclient,
    ioloop,
    options,
    web,
    gen
    )
from tornado.options import (
    define,
    options
    )
import tornado
import asyncmongo

define("port", default=8888, help="run on the given port", type=int)
define("mongodb_port", default=27017, help="run MongoDB on the given port", type=int)
define("mongodb_host", default='localhost', help="run MongoDB on the given hostname")
define("mongodb_database", default='scielo_network', help="Record accesses on the given database")
define("mongodb_max_connections", default=200, help="run MongoDB with the given max connections", type=int)
define("mongodb_max_cached", default=20, help="run MongoDB with the given max cached", type=int)
define("doi_prefix", default=None, help="indicates a txt file with each collection DOI prefix.", type=str)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/api/v1/article", ArticleHandler),
            (r"/api/v1/is_loaded", IsLoadedHandler),
       ]

        self.db = asyncmongo.Client(
            pool_id='articles',
            host=options.mongodb_host,
            port=options.mongodb_port,
            maxcached=options.mongodb_max_cached,
            maxconnections=options.mongodb_max_connections,
            dbname=options.mongodb_database
        )
        self.doi_prefix = {}
        if options.doi_prefix:
            with open(options.doi_prefix) as f:
                for line in f:
                    prefix = line.split("|")
                    self.doi_prefix[prefix[0]] = prefix[1]

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            )

        # Local is the default the default way that ratchet works.
        tornado.web.Application.__init__(self, handlers, **settings)


class IsLoadedHandler(tornado.web.RequestHandler):

    def _remove_callback(self, response, error):
        pass

    def _on_get_response(self, response, error):
        if error:
            raise tornado.web.HTTPError(500)

        if len(response) > 0:
            self.write('True')
        else:
            self.write('False')
        self.finish()

    @property
    def db(self):
        self._db = self.application.db
        return self._db

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        code = self.get_argument('code')
        self.db.articles.find({"code": code}, limit=1, callback=self._on_get_response)


class ArticleHandler(tornado.web.RequestHandler):

    def _remove_callback(self, response, error):
        pass

    def _on_get_response(self, response, error):
        if error:
            raise tornado.web.HTTPError(500)

        if len(response) > 0:
            self.render('scielo.xml')
            #self.write(str(response[0]))

        #self.finish()

    @property
    def db(self):
        self._db = self.application.db
        return self._db

    def post(self):
        code = self.get_argument('code')

        article_filename = '../output/isos/{0}/{0}_artigo.json'.format(code)
        title_filename = '../output/isos/{0}/{0}_title.json'.format(code)
        bib4cit_filename = '../output/isos/{0}/{0}_bib4cit.json'.format(code)
        article = json.loads(open(article_filename).read())
        title = json.loads(open(title_filename).read())
        bib4cit = json.loads(open(bib4cit_filename).read())

        dict_data = {'article': article['docs'][0],
                     'title': title['docs'][0],
                     'citations': bib4cit['docs']
                    }
        self.db.articles.update(
            {'code': code},
            {'$set': dict_data},
            safe=False,
            upsert=True
        )

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        def _on_response(response, error):
            if error:
                raise tornado.web.HTTPError(500)

            if len(response) > 0:
                if format == 'xml':
                    self.set_header('Content-Type', 'application/xml')
                    self.render('scielo.xml', code=code, data=response[0], doi_prefix=self.application.doi_prefix)
                else:
                    self.write(str(response[0]))
                    self.finish()

        code = self.get_argument('code')
        format = self.get_argument('format')
        self.db.articles.find({"code": code}, {"_id": 0}, limit=1, callback=_on_response)

if __name__ == '__main__':
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()