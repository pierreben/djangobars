from django.template import TemplateDoesNotExist
from django.template.loaders.base import Loader
from ..base import HandlebarsTemplate

class BaseHandlebarsLoader(Loader):
    """
    Base loader for Handlebars templates. Just override the load_template method
    to use the get_template_from_string method in the djangobars.template.loader
    module instead of the one in the core Django template codebase.
    """

    def get_template(self, template_name, skip=None):
        """
        Call self.get_template_sources() and return a Template object for
        the first template matching template_name. If skip is provided, ignore
        template origins in skip. This is used to avoid recursion during
        template extending.
        """
        tried = []

        for origin in self.get_template_sources(template_name):
            if skip is not None and origin in skip:
                tried.append((origin, 'Skipped'))
                continue

            try:
                contents = self.get_contents(origin)
            except TemplateDoesNotExist:
                tried.append((origin, 'Source does not exist'))
                continue
            else:
                return HandlebarsTemplate(contents, origin)

        raise TemplateDoesNotExist(template_name, tried=tried)

    def get_template_contents(self, template_name, skip=None):
        tried = []

        for origin in self.get_template_sources(template_name):
            if skip is not None and origin in skip:
                tried.append((origin, 'Skipped'))
                continue

            try:
                contents = self.get_contents(origin)
            except TemplateDoesNotExist:
                tried.append((origin, 'Source does not exist'))
                continue
            else:
                return contents

        raise TemplateDoesNotExist(template_name, tried=tried)
