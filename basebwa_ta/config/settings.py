from os import path

from basebwa.config.settings import Default as BaseDefaults

basedir = path.dirname(path.dirname(__file__))
app_package = path.basename(basedir)

class Default(BaseDefaults):
    def init(self):
        BaseDefaults.init(self, app_package, basedir)

        self.supporting_apps.append('basebwa')

        self.init_components()
        self.init_routing()

        ################################################################
        # DATABASE
        #######################################################################
        self.db.url = 'sqlite://'
        self.db.echo = False

        #######################################################################
        # TEMPLATES
        #######################################################################
        self.template.admin = 'testing.html'

    def init_routing(self):
        self.add_route('/ft1', endpoint='FormTest1')
        self.add_route('/ft2', endpoint='FormTest2')
        self.add_route('/ft2/<cancel_type>', endpoint='FormTest2')
        self.add_route('/widget/<action>', endpoint='WidgetCrud')
        self.add_route('/widget/<action>/<int:objid>', endpoint='WidgetCrud')
        self.add_route('/widget-auth/<action>', endpoint='WidgetCrudDeletePerm')
        self.add_route('/widget-auth/<action>/<int:objid>', endpoint='WidgetCrudDeletePerm')
        self.add_route('/admin-templating/pc-block', endpoint='admin_templating_primary_block.html')
        self.add_route('/control-panel', endpoint='apputil:DynamicControlPanel')

class Dev(Default):
    def init(self):
        Default.init(self)
        self.apply_dev_settings()

class Test(Default):
    def init(self):
        Default.init(self)
        self.apply_test_settings()
