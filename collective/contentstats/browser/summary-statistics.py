from DateTime import DateTime
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName


class Data(BrowserView):
    """View class providing the data for the summary statistics"""

    def catalog(self):
        return getToolByName(self, 'portal_catalog')

    def getTypes(self):
        """Return a list of dictionaries of format
        {'portal_type': <some type>, 'number' : <number of items>}
        """
        ct = self.catalog()
        existing_types = ct.uniqueValuesFor('portal_type') 
        result = []
        ct_arg = {}
        search_path = self.get_search_path()
        if search_path:
            ct_arg['path'] = search_path
        for t in existing_types:
            ct_arg['portal_type'] = t
            result.append(dict(portal_type = t,
                               number = len(ct(ct_arg))
                               ))
        return result

    def getStates(self):
        """Return a list of dictionaries of format
        {'state': <some state>, 'number' : <number of items in state>}
        """
        ct = self.catalog()
        existing_states = ct.uniqueValuesFor('review_state') 
        result = []
        ct_arg = {}
        search_path = self.get_search_path()
        if search_path:
            ct_arg['path'] = search_path
        for s in existing_states:
            ct_arg['review_state'] = s
            result.append(dict(state = s,
                               number = len(ct(ct_arg))
                               ))
        return result

    def getCount(self, portal_type, review_state):
        """Return the number of content items of type <portal_type> in state
        <review_state>"""
        ct = self.catalog()
        ct_arg = { 'portal_type': portal_type, 'review_state': review_state }
        search_path = self.get_search_path()
        if search_path:
            ct_arg['path'] = search_path
        return len(ct(ct_arg))

    def now(self):
        """The current date and time"""
        return DateTime().ISO()

    def total(self):
        """The total number of content items"""
        return len(self.catalog()())

    def get_search_path(self):
        return self.request.get('search_path', '')

    def extra_search_criterias(self):
        """A view helper method to build extra criterias in the query string"""
        # There may be no extra criteria or more than one criterias.
        # And this first emtpy string controls whether a & character appears
        #   at the front of returning string in the latter case.
        # I would like to keep the URL clean.
        criterias = ['']
        path = self.get_search_path()
        if path:
            criterias.append('path=%s' % path)
        return '&'.join(criterias)

class Export(Data):
    """
    Provide the statistics data in CSV format for download
    """
    
    def csv(self, line_sep="\n\r", separator=", "):
        """Export the data matrix to CSV (Comma Separated Values) format"""

        lines = []

        line = ['Portal Type|Review State']
        for s in self.getStates():
            line.append(s['state'])
        line.append('total')
        lines.append(separator.join(line))
            
        for t in self.getTypes():
            line = ["%s"%t['portal_type']]
            for s in self.getStates():
                c = self.getCount(t['portal_type'],s['state'])
                line.append('%s'%c)
            line.append("%s"%t['number'])
            lines.append(separator.join(line))

        line = ['total']
        for s in self.getStates():
            line.append("%s"%s['number'])
        line.append("%s"%self.total())
        lines.append(separator.join(line))

        response = line_sep.join(lines)

        self.request.response.setHeader('Content-Type', 'application/x-msexcel')
        self.request.response.setHeader("Content-Disposition", 
                                        "inline;filename=contentstatistics.csv")
        
        return response
