from paste.script.templates import Template, var
from paste.util.template import paste_script_template_renderer
from blazeutils import randchars

class ProjectTemplate(Template):

    _template_dir = ('basebwa', 'lib/paster_tpls/project')
    template_renderer = staticmethod(paste_script_template_renderer)
    summary = "A basic blazeweb project using basebwa as a supporting app"
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

    _template_dir = ('basebwa', 'lib/paster_tpls/module')
    template_renderer = staticmethod(paste_script_template_renderer)
    summary = "A blazeweb application module built in basebwa style"
    
    def post(self, command, output_dir, vars):
        print ''
        print '-'*70
        print 'Action Required: enabled module in settings.py'
        print '-'*70
        print 'self.modules.%s.enabled = True' % vars['modname']