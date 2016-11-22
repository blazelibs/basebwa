from blazeweb.globals import user
from blazeweb.routing import url_for

from webgrid import Column, DateTimeColumn
from webgrid.blazeweb import Grid
from webhelpers2.html import literal
from webhelpers2.html.tags import link_to

from basebwa_ta.model import orm


class WidgetGrid(Grid):
    endpoint = 'WidgetCrud'

    @property
    def has_delete(self):
        return True

    class ActionColumn(Column):
        has_edit = True

        @property
        def has_delete(self):
            return self.grid.has_delete

        def extract_data(self, rec):
            edit_link = ''
            if self.has_edit:
                edit_link = link_to(
                    '(edit)',
                    url_for(
                        self.grid.endpoint,
                        action='edit',
                        objid=rec.id,
                        session_key=self.grid.session_key
                    ),
                    class_='edit_link',
                    title='edit record'
                )
            delete_link = ''
            if self.has_delete:
                delete_link = link_to(
                    '(delete)',
                    url_for(
                        self.grid.endpoint,
                        action='delete',
                        objid=rec.id,
                        session_key=self.grid.session_key
                    ),
                    class_='delete_link',
                    title='delete record'
                )
            return literal(
                '{0}{1}'.format(
                    delete_link,
                    edit_link,
                )
            )

    ActionColumn('Actions', orm.Widget.id)
    Column('Type', orm.Widget.widget_type)
    Column('Color', orm.Widget.color)
    Column('Quantity', orm.Widget.quantity)
    DateTimeColumn('Created', orm.Widget.createdts)
    DateTimeColumn('Last Updated', orm.Widget.updatedts)


class WidgetAuthGrid(WidgetGrid):
    endpoint = 'WidgetCrudDeletePerm'

    @property
    def has_delete(self):
        return user.has_perm('widget-delete')
