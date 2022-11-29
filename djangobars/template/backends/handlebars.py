import pybars
from django.template.backends.base import BaseEngine
from django.conf import settings
from ..engine import Engine
from ..base import HandlebarsTemplate


class HandleBars(BaseEngine):

    # Name of the subdirectory containing the templates for this engine
    # inside an installed application.
    app_dirname = 'handlebars'

    def __init__(self, params):
        params.pop('OPTIONS', None)
        super().__init__(params)

        self.engine = Engine(self.dirs, self.app_dirs)
        self.compiler = pybars.Compiler()
        self.file_charset = 'utf-8'

    def get_template(self, template_name):
        return self.engine.get_template(template_name)


