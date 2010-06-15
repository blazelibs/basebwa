from os import path
from settings import Dev as SettingsDev

class Dev(SettingsDev):
    """ this custom "user" class is designed to be used for
    user specific development environments.  It can be used like:
    
        `pysmvt serve dev`
    """
    def __init__(self):
        SettingsDev.__init__(self)
        self.emails.override = 'developer@example.com'
        self.emails.from_default = 'developer@example.com'
dev = Dev

# have to redefine this so its based on the correct class object
class Test(Dev):
    """ default profile when running tests """
    def __init__(self):
        # call parent init to setup default settings
        Dev.__init__(self)
        self.apply_test_settings()
test=Test

# have to redefine this so its based on the correct class object
class TestInspDb(Dev):
    """ default profile when running tests """
    def __init__(self):
        # call parent init to setup default settings
        Dev.__init__(self)
        self.apply_test_settings()
        # uncomment this if you want to use a database you can inspect
        self.db.url = 'sqlite:///%s' % path.join(self.dirs.data, 'test_application.db')
testinspdb=TestInspDb