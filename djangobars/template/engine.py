from django.core.exceptions import ImproperlyConfigured
from django.template.exceptions import TemplateDoesNotExist
from django.utils.functional import cached_property
from django.utils.module_loading import import_string


class Engine:
    default_builtins = []

    def __init__(self, dirs=None, app_dirs=False, context_processors=None,
                 debug=False, loaders=None, string_if_invalid='',
                 file_charset='utf-8', libraries=None, builtins=None, autoescape=True):
        if dirs is None:
            dirs = []
        if context_processors is None:
            context_processors = []
        if loaders is None:
            loaders = ['djangobars.template.loaders.filesystem.Loader']
            if app_dirs:
                loaders += ['djangobars.template.loaders.app_directories.Loader']
        else:
            if app_dirs:
                raise ImproperlyConfigured(
                    "app_dirs must not be set when loaders is defined.")

        if libraries is None:
            libraries = {}
        if builtins is None:
            builtins = []

        self.dirs = dirs
        self.app_dirs = app_dirs
        self.autoescape = autoescape
        self.context_processors = context_processors
        self.debug = debug
        self.loaders = loaders
        self.string_if_invalid = string_if_invalid
        self.file_charset = file_charset
        self.libraries = libraries
        self.template_libraries = self.get_template_libraries(libraries)
        self.builtins = self.default_builtins + builtins
        self.template_builtins = self.get_template_builtins(self.builtins)

    @cached_property
    def template_loaders(self):
        return self.get_template_loaders(self.loaders)

    def get_template_builtins(self, builtins):
        return [import_library(x) for x in builtins]

    def get_template_libraries(self, libraries):
        loaded = {}
        for name, path in libraries.items():
            loaded[name] = import_library(path)
        return loaded

    def get_template_loaders(self, template_loaders):
        loaders = []
        for template_loader in template_loaders:
            loader = self.find_template_loader(template_loader)
            if loader is not None:
                loaders.append(loader)
        return loaders

    def find_template_loader(self, loader):
        if isinstance(loader, (tuple, list)):
            args = list(loader[1:])
            loader = loader[0]
        else:
            args = []

        if isinstance(loader, str):
            loader_class = import_string(loader)
            return loader_class(self, *args)
        else:
            raise ImproperlyConfigured(
                "Invalid value in template loaders configuration: %r" % loader)

    def find_template(self, name, dirs=None, skip=None):
        tried = []
        for loader in self.template_loaders:
            try:
                template = loader.get_template(name, skip=skip)
                return template, template.origin
            except TemplateDoesNotExist as e:
                tried.extend(e.tried)
        raise TemplateDoesNotExist(name, tried=tried)

    def get_template(self, template_name):
        """
        Return a compiled Template object for the given template name,
        handling template inheritance recursively.
        """
        template, origin = self.find_template(template_name)
        # if not hasattr(template, 'render'):
        #     # template needs to be compiled
        #     template = HandlebarsTemplate(template, origin, template_name, engine=self)
        return template
