from pysmvt import appimportauto
appimportauto('base', 'PublicSnippetView')

class FilterControls(PublicSnippetView):
    def default(self, datagrid=None):
        self.assign('datagrid', datagrid)

class SortControls(PublicSnippetView):
    def default(self, datagrid=None):
        self.assign('datagrid', datagrid)

class PagerControlsUpper(PublicSnippetView):
    def default(self, datagrid=None):
        self.assign('datagrid', datagrid)

class PagerControlsLower(PublicSnippetView):
    def default(self, datagrid=None):
        self.assign('datagrid', datagrid)

class Everything(PublicSnippetView):
    def default(self, datagrid=None):
        self.assign('datagrid', datagrid)