from pysmvt import getview
from pysmvt.htmltable import Table, Col, Link, DateTime, A
import actions
from pysutils import pprint

def audit_record_display(identifier):
    t = Table(class_='dataTable')
    t.createdts = DateTime('Date', format='%m/%d/%Y', width_th='20%')
    t.user_id = Col('User', extractor=lambda x: ('%s %s' % (x.user.name_first or '', x.user.name_last or '')).strip() or x.user.login_id, width_th='20%')
    t.comments = Col('Comments')
    return t.render(actions.get_audit_record_list(identifier))