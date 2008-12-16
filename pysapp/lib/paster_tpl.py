from paste.script.templates import Template, var
from paste.util.template import paste_script_template_renderer

class ProjectTemplate(Template):

    _template_dir = ('pysapp', 'lib/paster_tpls/pysapp')
    template_renderer = staticmethod(paste_script_template_renderer)
    summary = "A basic pysmvt project using pysapp as a supporting app"
    requires = ['pylons']
    vars = [
        var('description', 'One-line description of the package'),
        var('author', 'Your name'),
        var('programmer_email', 'Your email'),
    ]
    
    def pre(self, command, output_dir, vars):
        # convert user's name into a username var
        author = vars['author']
        vars['username'] = author.split(' ')[0].capitalize()