from lxml import etree
from StringIO import StringIO
import sys
import urllib2

schema = StringIO(open('journalpublishing3.xsd').read())
xml = StringIO(unicode(urllib2.urlopen(sys.argv[1]).read(), 'iso-8859-1'))
print xml
xmlschema_doc = etree.parse(schema)
xmlschema = etree.XMLSchema(xmlschema_doc)

# Loading XML File
xml = etree.parse(xml)
print u'validating: ' + sys.argv[1]
if not xmlschema.validate(xml):
    xmlschema.assertValid(xml)
else:
    print 'validated'
