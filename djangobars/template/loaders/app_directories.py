import sys
from django.template.loaders.app_directories import Loader as CoreLoader
from django.template.utils import get_app_template_dirs
from .base import BaseHandlebarsLoader
from ... import settings

# At compile time, cache the directories to search.
fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
app_template_dirs = []
app_dir_name = getattr(settings, 'HANDLEBARS_APP_DIRNAME', 'templates')

app_template_dirs = get_app_template_dirs('templates')


class Loader(BaseHandlebarsLoader, CoreLoader):

    def get_template_sources(self, template_name):
        """
        Returns the absolute paths to "template_name", when appended to each
        directory in "template_dirs". Any paths that don't lie inside one of the
        template dirs are excluded from the result set, for security reasons.
        """

        if self.dirs is None:
            self.dirs = app_template_dirs

        return super(Loader, self).get_template_sources(template_name)
