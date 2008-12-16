from paste.script.templates import Template, var
from paste.util.template import paste_script_template_renderer
from pysutils import randchars

class ProjectTemplate(Template):

    _template_dir = ('pysapp', 'lib/paster_tpls/project')
    template_renderer = staticmethod(paste_script_template_renderer)
    summary = "A basic pysmvt project using pysapp as a supporting app"
    vars = [
        var('description', 'One-line description of the package'),
        var('author', 'Your name'),
        var('programmer_email', 'Your email'),
    ]
    
    def pre(self, command, output_dir, vars):
        # convert user's name into a username var
        author = vars['author']
        vars['username'] = author.split(' ')[0].capitalize()
        vars['password'] = randchars(6)
        
    def post(self, command, output_dir, vars):
        print ''
        print '-'*70
        print 'Login Details'
        print '-'*70
        print 'admin & profile user: %s' % vars['username'].lower()
        print 'admin password: %s' % vars['password']
        
class ModuleTemplate(Template):

    _template_dir = ('pysapp', 'lib/paster_tpls/module')
    template_renderer = staticmethod(paste_script_template_renderer)
    summary = "A pysmvt application module built in pysapp style"
    
    def post(self, command, output_dir, vars):
        print ''
        print '-'*70
        print 'Action Required: enabled module in settings.py'
        print '-'*70
        print 'self.modules.%s.enabled = True' % vars['modname']