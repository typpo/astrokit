ALLOWED_KEYWORDS = set([
    'REVISEDDATA',
    'OBJECTNUMBER',
    'OBJECTNAME',
    'MPCDESIG',
    'CONTACTNAME',
    'CONTACTINFO',
    'OBSERVERS',
    'OBSLONGITUDE',
    'OBSLATITUDE',
    'SESSIONDATE',
    'SESSIONTIME',
    'FILTER',
    'MAGBAND',
    'STANDARD',
    'DIFFERMAGS',
    'LTCTYPE',
    'LTCDAYS',
    'LTCAPP',
    'REDUCEDMAGS',
    'UCORMAG',
    'OBJECTRA',
    'OBJECTDEC',
    'PHASE',
    'PABL',
    'PABB',
    'CICORRECTION',
    'CIBAND',
    'CITARGET',
    'PUBLICATION',
    'BIBCODE',
    'DELIMITER',
    'COMMENT',
])

REQUIRED_KEYWORDS = set([
    'CONTACTINFO',
    'CONTACTNAME',
    'DELIMITER',
    'FILTER',
    'OBJECTNAME',
    'OBJECTNUMBER',
    'OBSERVERS',
    'SESSIONDATE',
    'SESSIONTIME',
])

class AlcdefWriter(object):
    def __init__(self):
        self.metadata = {}
        self.starid = 1 # ID for metadata of comparison star
        self.comments = []
        self.datas = []

    def set(self, key, value):
        if key in ALLOWED_KEYWORDS:
            self.metadata[key] = value
        else:
            raise KeyError('Not a valid ALCDEF key: %s' % key)

    def add_comment(self, comment):
        self.comments.append(comment)

    def add_comparisonstar(self, pci='', dec='', name='', mag='', pra=''):
        self.metadata['COMPCI' + starid] = pci
        self.metadata['COMDEC' + starid] = dec
        self.metadata['COMNAME' + starid] = name
        self.metadata['COMMAG' + starid] = mag
        self.metadata['COMPRA' + starid] = pra
        self.starid += 1

    def add_data(self, jd, mag, magerr=None, airmass=None):
        data = "%s | %s" % (str(jd), mag)
        if magerr:
            data += " | %s" % (magerr)
        if airmass:
            data += " | %s" % (airmass)
        self.datas.append(data)

    def tostring(self):
        missing_required = REQUIRED_KEYWORDS.difference(set(self.metadata.keys()))
        if len(missing_required) > 0:
            return missing_required

        formatted_content = 'STARTMETADATA\n'
        for k, v in self.metadata.iteritems():
            formatted_content += "%s=%s\n" % (k, v)
        for v in self.comments:
            formatted_content += "COMMENT=%s\n" % v
        formatted_content += 'ENDMETADATA\n'

        for v in self.datas:
            formatted_content += "DATA=%s\n" % v
        formatted_content += 'ENDDATA\n'

        return formatted_content