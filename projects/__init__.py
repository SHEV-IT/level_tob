from abstract import Bot
import os
import imp
import inspect
import sys
import constants as c

modules = dict()
d = os.path.dirname(__file__)


def get_subclass(mod, cls):
    for name, obj in inspect.getmembers(mod):
        if hasattr(obj, "__bases__") and cls in obj.__bases__:
            return obj


for project_id in c.VK_PROJECTS:
    project_name = c.VK_PROJECTS[project_id]['name']
    project_module = c.VK_PROJECTS[project_id].get('module', project_name)
    sys.modules.pop(project_module, None)  # prevent loading cached module
    module = __import__(project_module, globals(), locals(), [], -1)
    bot_class = get_subclass(module, Bot)
    if bot_class:
        modules[project_name] = bot_class
