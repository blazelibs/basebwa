from pysmvt import getview
from pysmvt.htmltable import Table, Col, Link, DateTime, A
from pysmvt.routing import url_for
import actions

def audit_record_display(identifier, diff_view):
    t = Table(class_='dataTable')
    t.createdts = DateTime('Date', format='%m/%d/%Y', width_th='20%')
    t.user_id = Col('User', extractor=lambda x: ('%s %s' % (x.user.name_first or '', x.user.name_last or '')).strip() or x.user.login_id, width_th='20%')
    t.comments = Col('Comments')
    t.id = Link('Diff', validate_url=False, urlfrom=lambda row: url_for(diff_view, rev1=row.id))
    return t.render(actions.get_audit_record_list(identifier))