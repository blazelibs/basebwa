from blazeweb import db
from sqlitefktg4sa import auto_assign
from blazeweb import commands as cmds
from blazeweb import modimport, appimport
from blazeweb.script import console_broadcast

def action_module(modname='', template=('t', 'basebwa'),
        interactive=True, verbose=False, overwrite=True):
    """ creates a new module file structure (basebwa default)"""
    cmds.action_module(modname, template, interactive, verbose, overwrite)

    