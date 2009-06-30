"""

# Data Grid Notes #

## Column Types ##

A column is either a TableColumn or a DataColumn. A TableColumn is a column that
can possibly, but not necessarily, be rendered in the HTML table. A
DataColumn column is a column in the result set, but which can not be rendered
in the table. A DataColumn can be used in filters, sorts, and groupings.

The first argument passed to DataColumn is a string. The first argument passed
to DataColumn should be a pysmvt.htmltable.Col instance.
    
    from pysmvt.htmltable import Col
    TableColumn(Col('My Field'), ... )
    DataColumn('My Field', ... )

## Selecting Columns For Table ##

Not every table column needs to be displayed in the table by default:

    TableColumn(Col('Foo'), ... )
    TableColumn(Col('Bar'), ... )
    TableColumn(Col('Baz'), show=False, ... )
    
"Baz" column is not rendered in the table by default, but can be shown if
selected by the user.

## Paging ##

Defaults are set on the DataGrid object:

    DataGrid('page_size'=20, 'page_default'=1, 'page_size_editable'=True)
    
Pretty self explanatory.  If you don't want the user to be able to select the
page size, set page_size_editable = False.

## Sorting ##

Sorting can be accomplished by making the table header a hyperlink or by giving
a secondary drop-down for sorting:
    
    TableColumn(Col('Foo'), sort='header', ... ) # default for table columns
    TableColumn(Col('Foo'), sort='box', ... )
    TableColumn(Col('Foo'), sort='both', ... )
    DataColumn('Foo', sort=None, ... ) # default for RSO columns
    
The first option makes a hyperlink in the table header for sorting.  The second
option creates two entries in the secondary sort box 'Foo ASC', 'Foo DESC'.

Additional sort options can be added to the secondary sort box:

    dt = DataGrid(...)
    dt.add_sort_opt('custom sort ASC', 'field1 ASC', 'field2 ASC')
    dt.add_sort_opt('custom sort DESC', 'field1 DESC', 'field2 DESC')
    
## Grouping ##

Not to be confused with SQL GROUP BY, this simply breaks the results into
multiple tables based on the selected column.
    
    TableColumn(Col('Foo'), group_opt=False, ... ) # default
    TableColumn(Col('Bar'), group_opt=True, ... )
    
When using paging with grouping, keep in mind that paging takes precidence.

## Filtering ##

The following filter types are avilable:
    
    * Text Box w/ contains, doesn't contain, begins with, ends with, is, is not
    * Date Range w/ start and end dates
    * Boolean
    * Single Select w/ is, is not
    * Multi Select w/ in, not in
    * Multi Checkboxes

For single select, multi select, and multi checkboxes, a filter_options
parameter is required.

"""

class DataColumn(object)
    pass

class TableColumn(DataColumn)
    pass

class DataGrid(object)
    pass

class QueryBuilder(object)
    pass