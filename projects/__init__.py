from abstract import Bot
import os
import imp
import inspect
import sys
import types
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

    module_name = 'projects.%s' % project_module
    # get a reference to each loaded module
    loaded_package_modules = dict([
                                      (key, value) for key, value in sys.modules.items()
                                      if key.startswith(module_name) and isinstance(value, types.ModuleType)])

    # delete references to these loaded modules from sys.modules
    for key in loaded_package_modules:
        del sys.modules[key]

    module = __import__(project_module, globals(), locals(), [], -1)
    bot_class = get_subclass(module, Bot)
    if bot_class:
        modules[project_name] = bot_class
