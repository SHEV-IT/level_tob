from abstract import Bot
import os
import inspect
import sys
import constants as c

modules = dict()
d = os.path.dirname(__file__)


def get_subclass(mod, cls):
    for name, obj in inspect.getmembers(mod):
        if hasattr(obj, "__bases__") and cls in obj.__bases__:
            return obj


def get_module_files(module_path):
    ext = '.py'
    names = [os.path.join(module_path, x) for x in os.listdir(module_path)]
    files = filter(lambda x: x.endswith(ext) and os.path.isfile(x), names)
    dirs = filter(lambda x: os.path.isdir(x) and os.path.exists(os.path.join(x, '__init__.py')), names)

    res = ['.'.join(x[:-len(ext)].split(os.sep)) for x in files]
    for x in dirs:
        res.extend(get_module_files(x))

    res.append('.'.join(module_path.split(os.sep)))
    return res


imported = dict()
for project_id in c.VK_PROJECTS:
    project_name = c.VK_PROJECTS[project_id]['name']
    project_module = c.VK_PROJECTS[project_id].get('module', project_name)

    if project_module not in imported:
        module_path = os.path.join('projects', project_module)

        # get a reference to each module
        loaded_package_modules = get_module_files(module_path)

        # delete references to these loaded modules from sys.modules
        for key in loaded_package_modules:
            sys.modules.pop(key, None)

        module = __import__(project_module, globals(), locals(), [], -1)
        bot_class = get_subclass(module, Bot)
        if bot_class:
            modules[project_name] = bot_class
            imported[project_module] = bot_class
    else:  # multiple projects - one bot
        modules[project_name] = imported[project_module]
