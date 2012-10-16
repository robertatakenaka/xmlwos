class ShineData(object):

    def __init__(self, response, doi_prefix, article_types, journal_subjects, scielonet):
        self.data = response
        self.article_types = article_types
        self.journal_subjects = journal_subjects
        self.scielonet = scielonet
        if doi_prefix:
            self.doi_prefix = doi_prefix
        


    @property
    def article(self):
        article = {}
              
        article['teste'] = ''
        issn = self.data['title']['v400'][0]['_'].upper()
        if issn in self.journal_subjects.keys():
            article['journal-subjects'] = self.journal_subjects[issn]
        
        if 'v71' in self.data['article']:
            article_type = self.data['article']['v71'][0]['_']
        else:
            article_type = 'nd'
        if article_type in self.article_types.keys():
            article['article_type'] = self.article_types[article_type]
        else:
            article['article_type'] = self.article_types['nd']

        article['original_language'] = self.data['article']['v40'][0]['_']
        article['journal-id'] = self.data['title']['v930'][0]['_'].lower()
        article['issn'] = issn
        article['article-id'] = self.data['article']['v880'][0]['_'].upper()

        if 'v690' in self.data['title']:
            article['scielo-url'] = self.data['title']['v690'][0]['_']
        if 'v691' in self.data['title']:
            article['scielonetid'] = self.data['title']['v691'][0]['_']
            if not 'scielo-url' in article:
                k = 'x'
                if '1' in article['scielonetid']:
                    k = str(article['scielonetid'].find('1')+1)
                if k in self.scielonet.keys():
                    article['scielo-url'] = self.scielonet[k]
            #article['teste'] += article['scielonetid'] + '\n' + ', '.join(self.scielonet.keys()) + '\n' + ','.join(self.scielonet.values())
        # Defining the DOI number
        get_doi_from_xml = False
        if 'v237' in self.data['article']:
            article['article-id-doi'] = self.data['article']['v237'][0]['_']
        else:
            if self.doi_prefix and article['article-id'] in self.doi_prefix:
                if 'v881' in self.data['article']:
                    article['article-id-doi'] = "{0}/{1}".format(
                        self.doi_prefix[article['article-id']],
                        self.data['article']['v881'][0]['_'].upper()
                    )
                else:
                    article['article-id-doi'] = "{0}/{1}".format(
                        self.doi_prefix[article['article-id']],
                        self.data['article']['v880'][0]['_'].upper()
                    )
            else:
                if 'scielo-url' in article and 'article-id' in article: 
                    doi_url = "http://{0}/scielo.php?script=sci_isoref&pid={1}&debug=xml".format(article['scielo-url'], article['article-id'])
                    print(doi_url)
                    doi_xml = ''
                    try:
                        import urllib2
                        doi_xml = urllib2.urlopen(urllib2.Request(doi_url)).read()
                    except:
                        try:
                            import urllib.request 
                            doi_xml = urllib.request.urlopen(doi_url).read()
                        except:
                            doi_xml = ''
                    if len(doi_xml)>0:            
                        if 'DOI="' in doi_xml:
                            doi_xml = doi_xml[doi_xml.find('DOI="')+len('DOI="'):]
                            article['article-id-doi'] = doi_xml[0:doi_xml.find('"')]
                            


      
        if 'v100' in self.data['title']:
            article['journal-title'] = self.data['title']['v100'][0]['_']

        if 'v110' in self.data['title']:
            article['journal-subtitle'] = self.data['title']['v110'][0]['_']

        if 'v150' in self.data['title']:
            article['abbrev-journal-title'] = self.data['title']['v150'][0]['_']

        if 'v480' in self.data['title']:
            article['publisher-name'] = self.data['title']['v480'][0]['_']

        if 'v490' in self.data['title']:
            article['publisher-loc'] = self.data['title']['v490'][0]['_']

        if 'v31' in self.data['article']:
            article['volume'] = self.data['article']['v31'][0]['_']

        if 'v32' in self.data['article']:
            article['issue'] = self.data['article']['v32'][0]['_']

        # Supplement
        if 'v131' in self.data['article'] or 'v132' in self.data['article']:
            if 'v131' in self.data['article']:
                supplv = u"v. " + self.data['article']['v131'][0]['_']
            if 'v132' in self.data['article']:
                suppln = u"i. " + self.data['article']['v132'][0]['_']

            article['supplement'] = "Suppl. {0} {1}".format(supplv, suppln)

        # Pages
        if 'v14' in self.data['article']:
            if 'f' in self.data['article']['v14'][0]:
                article['fpage'] = self.data['article']['v14'][0]['f']
            if 'l' in self.data['article']['v14'][0]:
                article['lpage'] = self.data['article']['v14'][0]['l']

        # Article titles
        article['group-title'] = {}
        article['group-title']['article-title'] = {}
        article['group-title']['trans-title'] = {}
        for title in self.data['article']['v12']:
            if title['l'] == article['original_language']:
                article['group-title']['article-title'].setdefault(title['l'],
                    title['_']
                    )
            else:
                article['group-title']['trans-title'].setdefault(title['l'],
                    title['_']
                    )

        # Authors
        if 'v10' in self.data['article']:
            article['contrib-group'] = []
            if 'v10' in self.data['article']:  # for author
                for author in self.data['article']['v10']:
                    authordict = {}
                    if 's' in author:
                        authordict['surname'] = author['s']
                    if 'n' in author:
                        authordict['given-names'] = author['n']
                    if 'r' in author:
                        authordict['role'] = author['r']
                    if '1' in author:
                        authordict['xref'] = author['1']

                    article['contrib-group'].append(authordict)

        # Affiliations
        if 'v70' in self.data['article']:
            article['aff-group'] = []
            for affiliation in self.data['article']['v70']:
                affdict = {}
                affdict['index'] = affiliation['i']
                if 'c' in affiliation:
                    affdict['addr-line'] = affiliation['c']
                if '_' in affiliation:
                    affdict['institution'] = affiliation['_']
                if 'p' in affiliation:
                    affdict['country'] = affiliation['p']
                if 'e' in affiliation:
                    affdict['email'] = affiliation['e']
                article['aff-group'].append(affdict)

        # Publication date
        article['pub-date'] = {}
        if self.data['article']['v65'][0]['_'][6:8] != '00':
            article['pub-date']['day'] = self.data['article']['v65'][0]['_'][6:8]
        if self.data['article']['v65'][0]['_'][4:6] != '00':
            article['pub-date']['month'] = self.data['article']['v65'][0]['_'][4:6]
        article['pub-date']['year'] = self.data['article']['v65'][0]['_'][0:4]

        # Url
        if 'scielo-url' in article:
            article['self-uri'] = {}
            article['self-uri']['full-text-page'] = "http://{0}/scielo.php?script=sci_arttext&amp;pid={1}&amp;lng=en&amp;tlng=en".format(article['scielo-url'], article['article-id'])
            article['self-uri']['issue-page'] = "http://{0}/scielo.php?script=sci_issuetoc&amp;pid={1}&amp;lng=en&amp;tlng=en".format(article['scielo-url'], article['article-id'][0:18])
            article['self-uri']['journal-page'] = "http://{0}/scielo.php?script=sci_serial&amp;pid={1}&amp;lng=en&amp;tlng=en".format(article['scielo-url'], article['article-id'][1:10])

        # Abstract
        if 'v83' in self.data['article']:
            article['group-abstract'] = {}
            article['group-abstract']['abstract'] = {}
            article['group-abstract']['trans-abstract'] = {}
            for abstract in self.data['article']['v83']:
                if abstract['l'] == article['original_language']:
                    article['group-abstract']['abstract'].setdefault(
                        abstract['l'],
                        abstract['a']
                        )
                else:
                    article['group-abstract']['trans-abstract'].setdefault(
                        abstract['l'],
                        abstract['a']
                        )

        # Keyword
        if 'v85' in self.data['article']:
            article['kwd-group'] = {}
            for keyword in self.data['article']['v85']:
                if 'k' in keyword:
                    group = article['kwd-group'].setdefault(keyword['l'], [])
                    group.append(keyword['k'])
        
            
        return article

    @property
    def citations(self):
        citations = []
        for data in self.data['citations']:
            citation = {}

            if 'v701' in data:
                citation['order'] = data['v701'][0]['_']

            # Citation type [book, article]
            if 'v18' in data:
                citation['publication-type'] = 'book'
            elif 'v12' in data:
                citation['publication-type'] = 'article'
            elif 'v53' in data:
                citation['publication-type'] = 'conference'
            elif 'v45' in data:
                citation['publication-type'] = 'thesis'
            else:
                citation['publication-type'] = 'nd'
            # Journal Title instead of Book title in source element.
            if 'v30' in data:
                citation['source'] = data['v30'][0]['_']

            # Citation title
            if citation['publication-type'] == 'book':
                citation['source'] = data['v18'][0]['_']
                if 'v12' in data:
                    citation['chapter-title'] = data['v12'][0]['_']
            elif citation['publication-type'] == 'article':
                citation['article-title'] = data['v12'][0]['_']

            # Conference date
            if 'v54' in data:
                citation['conf-date'] = data['v54'][0]['_']

            # Coference loc
            if 'v56' in data or 'v57' in data:
                loc = []
                if 'v56' in data:
                    loc.append(data['v56'][0]['_'])
                    if 'l' in data['v56'][0]:
                        loc.append(data['v56'][0]['l'])
                if 'v57' in data:
                    loc.append(data['v57'][0]['_'])

                citation['conf-loc'] = ", ".join(loc)

            # Conference name
            if 'v53' in data:
                citation['conf-name'] = data['v53'][0]['_']

            # Conference sponsor
            if 'v52' in data:
                citation['conf-sponsor'] = data['v52'][0]['_']

            # Citation date
            if 'v65' in data:
                citation['date'] = {}
                if data['v65'][0]['_'][6:8] != '00':
                    citation['date']['day'] = data['v65'][0]['_'][6:8]
                if data['v65'][0]['_'][4:6] != '00':
                    citation['date']['month'] = data['v65'][0]['_'][4:6]
                citation['date']['year'] = data['v65'][0]['_'][0:4]

            # Edition
            if 'v63' in data:
                citation['edition'] = data['v63'][0]['_'][0:4]

            # URL
            if 'v37' in data:
                citation['uri'] = data['v37'][0]['_']

            # Pages
            if 'v14' in data:
                page_range = data['v14'][0]['_'].split('-')
                citation['fpage'] = page_range[0]
                if len(page_range) > 1:
                    citation['lpage'] = page_range[1]

            # Institution
            citation['institutions'] = []
            if 'v11' in data:
                citation['institutions'].append(data['v11'][0]['_'])
            if 'v17' in data:
                citation['institutions'].append(data['v17'][0]['_'])
            if 'v29' in data:
                citation['institutions'].append(data['v29'][0]['_'])
            if 'v50' in data:
                citation['institutions'].append(data['v50'][0]['_'])
            if 'v58' in data:
                citation['institutions'].append(data['v58'][0]['_'])

            # ISSN
            if 'v35' in data:
                citation['issn'] = data['v35'][0]['_']

            # ISBN
            if 'v69' in data:
                citation['isbn'] = data['v69'][0]['_']

            # Volume number
            if 'v31' in data:
                citation['volume'] = data['v31'][0]['_']

            # Issue number
            if 'v32' in data:
                citation['issue'] = data['v32'][0]['_']

            # Issue title
            if 'v33' in data:
                citation['issue-title'] = data['v33'][0]['_']

            # Issue part
            if 'v34' in data:
                citation['issue-part'] = data['v34'][0]['_']

            # Citation DOI
            if 'v237' in data:
                citation['object-id'] = data['v237'][0]['_']

            # Authors analitic
            if 'v10' in data or 'v16' in data:
                citation['person-group'] = []

            if 'v10' in data:
                for author in data['v10']:
                    authordict = {}
                    if 's' in author:
                        authordict['surname'] = author['s']
                    if 'n' in author:
                        authordict['given-names'] = author['n']

                    citation['person-group'].append(authordict)

            # Authors monographic
            if 'v16' in data:
                for author in data['v16']:
                    authordict = {}
                    if 's' in author:
                        authordict['surname'] = author['s']
                    if 'n' in author:
                        authordict['given-names'] = author['n']

                    citation['person-group'].append(authordict)

            if 'v25' in data:
                citation['series'] = data['v25'][0]['_']
            if 'v62' in data:
                citation['publisher-name'] = data['v62'][0]['_']

            # Publisher loc
            if 'v66' in data or 'v67' in data:
                loc = []
                if 'v66' in data:
                    loc.append(data['v66'][0]['_'])
                    if 'e' in data['v66'][0]:
                        loc.append(data['v66'][0]['e'])
                if 'v67' in data:
                    loc.append(data['v67'][0]['_'])

                citation['publisher-loc'] = ", ".join(loc)

            citations.append(citation)

        return citations
