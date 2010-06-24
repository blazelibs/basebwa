from settings import Default

class Dev(Default):
    """ default profile for command based actions """
    def init(self):
        Default.init(self)

        self.apply_dev_settings('devemail@example.com', 'myuser', 'password')
        self.emails.from_default = 'devemail@example.com'

        # beaker sessions
        self.init_beaker(timeout=60*60*24*7)

class Test(Dev):
    """ default profile when running tests """
    def init(self):
        # call parent init to setup default settings
        Dev.init(self)
        self.apply_test_settings()

        # uncomment this if you want to use a database you can inspect
        #from os import path
        #self.db.url = 'sqlite:///%s' % path.join(self.dirs.data, 'test_application.db')
        #self.assign_beaker_url()
