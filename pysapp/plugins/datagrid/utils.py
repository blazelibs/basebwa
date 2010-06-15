"""
See tests for example usage
"""
from decimal import Decimal, InvalidOperation
from dateutil.parser import parse
from sqlalchemy import types
from sqlalchemy.sql import select, not_, func
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy import schema
from pysmvt.utils import OrderedProperties, simplify_string, OrderedDict
from werkzeug import Request, cached_property, Href, MultiDict
from werkzeug.exceptions import BadRequest
from pysmvt import rg, getview
from pysmvt.htmltable import Table
from pysmvt.routing import current_url
from webhelpers.html import literal, escape

class SADeclarativeAttributeHelper(object):
    def __init__(self, sacol):
        self.saattr = sacol
    
    @property
    def type(self):
        return self.saattr.property.columns[0].type

class SATableColumnHelper(object):
    def __init__(self, sacol):
        self.sacol = sacol
        
    @property
    def type(self):
        return self.sacol.type

class DataColumn(object):
    def __init__(self, label, sacol, inresult=False, sort=None ):
        self.sacol = sacol
        if isinstance(sacol, InstrumentedAttribute):
            self.sacol_helper = SADeclarativeAttributeHelper(sacol)
        elif isinstance(sacol, schema.Column):
            self.sacol_helper = SATableColumnHelper(sacol)
        else:
            raise BadRequest('Expected SQLAlchemy declarative attribute or table column')
        self.label = label
        # gets set to true if this column needs to be in the returned result
        # set. Useful for things like an "ID" column that wouldn't be in the
        # table but you would need in the resultset so you could create
        # resultsets, etc.
        self.inresult = inresult
        self.sort = sort
        
    def __repr__(self):
        return "<DataColumn: %s" % self.label
        
class TableColumn(DataColumn):
    def __init__(self, tblcol, sacol, **kwargs):
        inresult = kwargs.pop('inresult', True)
        show = kwargs.pop('show', True)
        DataColumn.__init__(self, tblcol.header, sacol, inresult=inresult, **kwargs)
        self.tblcol = tblcol

class DataGrid(object):
    
    def __init__(self, executable, def_sort=None, def_filter=None,
                 rs_customizer=None, page=None, per_page=None, environ=None,
                 row_dec=None, **kwargs ):
        self.executable = executable
        self.rs_customizer = rs_customizer
        self.def_filter = def_filter
        self.def_sort = def_sort
        self.data_cols = OrderedDict()        
        self._filter_ons = OrderedDict()        
        self._table_cols = OrderedDict()
        self.sql_columns = []
        self.environ = environ
        self._request = None
        self._sortheaders = OrderedDict()
        self._sortdd = OrderedDict()
        self.page = page or 1
        self.per_page = per_page
        self._count = None
        self._records = None
        self._query = None
        self._fo_operators = ('eq', 'ne', 'lt', 'gt', 'lte', 'gte', 'contains')
        self._html_table = None
        self._filter_ons_selected = None
        self._filterons_op_selected = None
        self._base_query = None
        self._current_sortdd_ident = None
        self._html_table_attributes = kwargs
        self._current_sort_desc = False
        self._row_dec = row_dec
    
    def add_tablecol(self, tblcolobj, sacol, **kwargs):
        filter_on = kwargs.pop('filter_on', None)
        kwargs.setdefault('sort', 'header')
        tc = TableColumn(
                tblcolobj,
                sacol,
                **kwargs
            )
        self._add_col(tc, filter_on, kwargs)
        
    def add_col(self, label, sacol, **kwargs):
        filter_on = kwargs.pop('filter_on', None)
        dc = DataColumn(
                label,
                sacol,
                **kwargs
            )
        self._add_col(dc, filter_on, kwargs)
    
    def _add_col(self, dc, filter_on, kwargs):
        ident = self._col_ident(dc.label)
        self.data_cols[ident] = dc
        if filter_on:
            self._filter_ons[ident] = dc
        if isinstance(dc, TableColumn):
            self._table_cols[ident] = dc
        sorttype = kwargs.get('sort', None)
        if sorttype in ('header', 'both'):
            self._sortheaders[ident] = dc
        if sorttype in ('drop-down', 'both'):
            self.add_sort(dc.label + ' ASC', dc.sacol)
            self.add_sort(dc.label + ' DESC', dc.sacol.desc())
        
    def add_sort(self, label, *args):
        ident = simplify_string(label, replace_with='')
        self._sortdd[ident] = {'args':args, 'label':label}
    
    def _col_ident(self, label):
        ident = None
        count = 1
        while not ident or self.data_cols.has_key(ident):
            ident = simplify_string(label, replace_with='')
            if count > 1:
                ident = '%s%s' % (ident, count)
            count += 1
        return ident
    
    def get_select_query(self):
        for col in self.data_cols.values():
            if col.inresult:
                self.sql_columns.append(col.sacol)
        
        query = select(self.sql_columns)
        return query
     
    def base_query(self):
        if self._base_query is None:
            query = self.get_select_query()
            query = self._apply_filters(query)
            query = self._apply_sort(query)
            
            if self.rs_customizer:
                query = self.rs_customizer(query)
            
            self._base_query = query
        return self._base_query
    
    def get_query(self):
        if self._query is None:
            query = self.base_query()
            query = self._apply_paging(query)
            query = query.apply_labels()
            self._query = query
        return self._query
    
    def force_request_process(self):
        if self._query is None:
            self.get_query()
    
    def _req_obj(self):
        if self._request:
            return self._request
        if self.environ is not None:
            ro = Request(self.environ)
        else:
            ro = rg.request
        self._request = ro
        return self._request
    
    def _replace_environ(self, environ):
        self.environ = environ
        self._request = None
        self._query = None
        self._base_query = None
    
    def _sanitize_filter_input(self, ident, input):
        sahlpr = self._filter_ons[ident].sacol_helper
        if input.strip() == '':
            return None
        # if column is datetime, date, or time type, turn string
        # into a datetime object
        if isinstance(sahlpr.type, (types.DateTime, types.Date, types.Time)):
            try:
                return parse(input)
            except ValueError, e:
                if 'unknown string format' not in str(e):
                    raise
                raise BadRequest('Unknown date/time string "%s"' % input)
        elif isinstance(sahlpr.type, types.Integer):
            try:
                return int(input)
            except ValueError:
                raise BadRequest('"%s" was not an integer value' % input)
        elif isinstance(sahlpr.type, types.Float):
            try:
                return float(input)
            except ValueError:
                raise BadRequest('"%s" was not a float value' % input)
        elif isinstance(sahlpr.type, types.Numeric):
            try:
                return Decimal(input)
            except InvalidOperation:
                raise BadRequest('"%s" was not a decimal value' % input)
        return input
    
    def _apply_filters(self, query):
        args = self._req_obj().args
        filter_in_request = False
        use_like = False
        self._filter_ons_selected = None
        self._filterons_op_selected = None
        
        fokey = self._args_prefix('filteron')
        foopkey = self._args_prefix('filteronop')
        forkey = self._args_prefix('filterfor')
        if args.has_key(fokey):
            ident = args[fokey]

            if ident:
                if not self._filter_ons.has_key(ident):
                    raise BadRequest('The Filter On value "%s" is invalid' % ident)
            
                if not args.has_key(foopkey):
                    raise BadRequest('When using a filter, a "filteronop" value must also be sent')
                
                if not args.has_key(forkey):
                    raise BadRequest('When using a filter, a "filterfor" value must also be sent')
                    
                fsacol = self._filter_ons[ident].sacol
                ffor = self._sanitize_filter_input(ident, args[forkey])
                foop = args[foopkey]
                
                if ffor is None and foop in ('lt', 'gt', 'lte', 'gte'):
                    raise BadRequest('A blank value can only be used with "equal" or "not equal" operators')
                
                if foop not in self._fo_operators:
                    if foop:
                        raise BadRequest('The filter comparison operator "%s" is invalid' % foop)
                    else:
                        raise BadRequest('Please select a comparison operator for your filter')

                if foop == 'contains':
                    ffor = '%%%s%%'%ffor
                    use_like = True

                if isinstance(ffor, basestring) and '*' in ffor:
                    if foop in ('lt', 'gt', 'lte', 'gte'):
                        raise BadRequest('wildcards are invalid when using "less than" or "greater than"')
                    ffor = ffor.replace('*', '%')
                    use_like = True
                    
                if foop == 'lt':
                    query = query.where(fsacol < ffor)
                elif foop == 'lte':
                    query = query.where(fsacol <= ffor)
                elif foop == 'gt':
                    query = query.where(fsacol > ffor)
                elif foop == 'gte':
                    query = query.where(fsacol >= ffor)
                elif foop == 'eq' or foop == 'contains':
                    if use_like:
                        query = query.where(fsacol.like(ffor))
                    else:
                        query = query.where(fsacol == ffor)
                elif foop == 'ne':
                    if use_like:
                        query = query.where(not_(fsacol.like(ffor)))
                    else:
                        query = query.where(fsacol != ffor)
                
                self._filter_ons_selected = ident
                self._filterons_op_selected = foop
                filter_in_request = True
        
        if self.def_filter and not filter_in_request:
            query = self.def_filter(query)
        
        return query
    
    def _apply_sort(self, query):
        args = self._req_obj().args
        sort_in_request = False
        self._current_sort_header = None
        self._current_sort_desc = False
        self._current_sort_direction = None
        self._current_sortdd_ident = None
        
        # drop-down sorting (takes precedence over header sorting)
        sortkey = self._args_prefix('sortdd')
        ident = args.get(sortkey, None)
        if ident:
            if not self._sortdd.has_key(ident):
                raise BadRequest('The sort ident "%s" is invalid' % ident)
                
            sortargs = self._sortdd[ident]['args']
            query = query.order_by(*sortargs)
            
            sort_in_request = True
            self._current_sortdd_ident = ident
        else:
            # header sorting
            sortkey = self._args_prefix('sort')
            sortcol = args.get(sortkey, None)
            if sortcol:
            
                if sortcol.startswith('-'):
                    sortcol = sortcol[1:]
                    desc = True
                    self._current_sort_desc = True
                else:
                    desc = False
                
                if not self._sortheaders.has_key(sortcol):
                    raise BadRequest('The sort column "%s" is invalid' % sortcol)
                
                sortcolobj = self._sortheaders[sortcol].sacol
                if desc:
                    query = query.order_by(sortcolobj.desc())
                else:
                    query = query.order_by(sortcolobj)
                
                sort_in_request = True
                self._current_sort_header = sortcol

        # default sorting
        if self.def_sort and not sort_in_request:
            query = self.def_sort(query)
        
        return query    
    
    def _apply_paging(self, query):
        args = self._req_obj().args

        perpagekey = self._args_prefix('perpage')
        if args.has_key(perpagekey):
            try:
                per_page = int(args[perpagekey])
                if per_page < 1:
                    raise ValueError
            except ValueError:
                raise BadRequest('The perpage arg must be a positive integer')
            self.per_page = per_page
        
        pagekey = self._args_prefix('page')
        if args.has_key(pagekey):
            try:
                page = int(args[pagekey])
                if page < 1:
                    raise ValueError
            except ValueError:
                raise BadRequest('The page arg must be a positive integer')
            if page > self.pages:
                self.page = self.pages
            else:
                self.page = page

        if self.page and self.per_page:
            query = query.offset((self.page - 1) * self.per_page) \
                             .limit(self.per_page)

        return query
    
    def _args_prefix(self, key):
        return key

    @property
    def count(self):
        if not self._count:
            count_query = select([func.count()], from_obj=self.base_query().alias('main_query'))
            self._count = self.executable(count_query).scalar()
        return self._count

    @property
    def records(self):
        if not self._records:
            self._records = self.executable(self.get_query()).fetchall()
        return self._records

    has_previous = property(lambda x: x.page > 1)
    has_next = property(lambda x: x.page < x.pages)
    previous = property(lambda x: x.page - 1)
    next = property(lambda x: x.page + 1)
    
    @property
    def pages(self):
        if self.per_page is None:
            return 0
        return max(0, self.count - 1) // self.per_page + 1
    
    @property
    def html_table(self):
        self.force_request_process()
        
        def extractor_helper(row, label, extractor):
            if extractor:
                return extractor(row)
            else:
                return row[label]

        if not self._html_table:
            t = Table(row_dec = self._row_dec, **self._html_table_attributes)
            for ident, col in self._table_cols.items():
                
                # setup getting the correct column from the row data
                try:
                    label = col.sacol.__clause_element__()._label
                except AttributeError:
                    label = col.sacol._label
                col.tblcol.extractor = lambda row, label=label, extractor=col.tblcol.extractor: extractor_helper(row, label, extractor)
                
                # setup adding sort links to our headers
                col.tblcol.th_decorator = self._decorate_table_header(ident, col)
                
                # create the column on the HTML table
                setattr(t, ident, col.tblcol)
            self._html_table = t.render(self.records)

        return self._html_table
    
    @property
    def show_filter_controls(self):
        self.force_request_process()
        return len(self._filter_ons) > 0
    
    @property
    def html_filter_controls(self):
        return getview('datagrid:FilterControls', datagrid=self)
    
    def selected_filteron_opt(self, ident):
        self.force_request_process()
        if self._filter_ons_selected == ident:
            return ' selected="selected"'
        return ''
    
    def selected_filteronop_opt(self, op):
        self.force_request_process()
        if self._filterons_op_selected == op:
            return ' selected="selected"'
        return ''
    
    @property
    def value_filterfor(self):
        req = self._req_obj()
        fokey = self._args_prefix('filterfor')
        return req.args.get(fokey, '')
        
    @property
    def value_sort(self):
        req = self._req_obj()
        skey = self._args_prefix('sort')
        return req.args.get(skey, '')
    
    @property
    def show_sort_controls(self):
        self.force_request_process()
        return len(self._sortdd) > 0
    
    @property
    def html_sort_controls(self):
        return getview('datagrid:SortControls', datagrid=self)
    
    def selected_sortdd_opt(self, ident):
        self.force_request_process()
        if self._current_sortdd_ident == ident:
            return ' selected="selected"'
        return ''
    
    @property
    def show_pager_controls_upper(self):
        self.force_request_process()
        return self.page and self.pages
    
    def selected_page_opt(self, page):
        self.force_request_process()
        if self.page == page:
            return ' selected="selected"'
        return ''
    
    @property
    def html_pager_controls_upper(self):
        return getview('datagrid:PagerControlsUpper', datagrid=self)

    @property
    def value_perpage(self):
        return self.per_page

    @property
    def html_pager_controls_lower(self):
        return getview('datagrid:PagerControlsLower', datagrid=self)
    
    @property
    def show_pager_controls_lower(self):
        self.force_request_process()
        return self.page and self.pages
    
    @property
    def link_pager_first(self):
        return self._current_url(page=1)
    
    @property
    def link_pager_previous(self):
        return self._current_url(page=self.page-1)
    
    @property
    def link_pager_next(self):
        return self._current_url(page=self.page+1)
    
    @property
    def link_pager_last(self):
        return self._current_url(page=self.pages)       

    @property
    def html_everything(self):
        return getview('datagrid:Everything', datagrid=self)

    @property
    def url_reset(self):
        return self._current_url(
            filteron = None,
            filteronop = None,
            filterfor = None,
            page=None,
            perpage=None,
            sortdd = None,
            sort=None
        )

    @property
    def url_form_action(self):
        return self.url_reset

    def _decorate_table_header(self, ident=None, col=None ):
        def inner_decorator(todecorate):
            if col.sort in ('header', 'both'):
                if self._current_sort_header == ident:
                    if self._current_sort_desc:
                        desc_prefix = ''
                        link_class = 'sort-desc'
                        sortimg = '<img src="images/icons/sort_down.gif" width="9" height="5" alt="currently sorting desc" title="currently sorting desc" />'
                        linktitle = 'currently sorting desc, click to reverse'
                    else:
                        desc_prefix = '-'
                        link_class = 'sort-asc'
                        sortimg = '<img src="images/icons/sort_up.gif" width="9" height="5" alt="currently sorting asc" title="currently sorting asc" />'
                        linktitle = 'currently sorting asc, click to reverse'
                else:
                    desc_prefix = ''
                    link_class = ''
                    sortimg = ''
                    linktitle = ''
                    
                sortvalue = '%s%s' % (desc_prefix,ident)
                url = escape(self._current_url(sort=sortvalue))
                return literal('<a href="%s" class="%s" title="%s">%s</a>%s' % (url, link_class, linktitle, todecorate, sortimg))
            else:
                return todecorate
        return inner_decorator
    
    def _current_url(self, **kwargs):
        req = self._req_obj()
        href = Href(current_url(strip_querystring=True, strip_host=True, environ=req.environ), sort=True)
        
        args = MultiDict(req.args)
        # multidicts extend, not replace, so we need to get rid of the keys first
        for key in kwargs.keys():
            try:
                del args[key]
            except KeyError:
                pass
        
        # convert to md first so that if we have lists in the kwargs, they
        # are converted appropriately
        args.update(MultiDict(kwargs))
        return href(args)