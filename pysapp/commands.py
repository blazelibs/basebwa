from pysmvt import db
from sqlitefktg4sa import auto_assign
from pysmvt import commands as cmds
from pysmvt import modimport, appimport
from pysmvt.script import console_broadcast

def action_module(modname='', template=('t', 'pysapp'),
        interactive=True, verbose=False, overwrite=True):
    """ creates a new module file structure (pysapp default)"""
    cmds.action_module(modname, template, interactive, verbose, overwrite)

    