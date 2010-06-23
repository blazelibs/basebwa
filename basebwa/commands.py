from blazeweb.globals import commands as cmds

def action_module(modname='', template=('t', 'basebwa'),
        interactive=True, verbose=False, overwrite=True):
    """ creates a new module file structure (basebwa default)"""
    cmds.action_module(modname, template, interactive, verbose, overwrite)

    