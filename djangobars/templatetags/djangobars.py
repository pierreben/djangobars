from django import VERSION as DJANGO_VERSION
from django.template.base import TextNode, Node, Variable, TemplateSyntaxError
from django.template.library import Library
from django.template.utils import EngineHandler
from ..template.loaders.app_directories import Loader

register = Library()
engines = EngineHandler()


class IncludeHandlebarsNode(Node):
    context_key = '__include_context'

    def __init__(self, template, *args, extra_context=None, isolated_context=False, **kwargs):
        self.template = Variable(template)
        self.extra_context = extra_context or {}
        self.isolated_context = isolated_context
        super().__init__(*args, **kwargs)

    def render(self, context):
        """
        Render the specified template and context. Cache the template object
        in render_context to avoid reparsing and loading when used in a for
        loop.
        """
        template = self.template.resolve(context)
        # Does this quack like a Template?
        if not callable(getattr(template, 'render', None)):
            # If not, try the cache and get_template().
            template_name = template
            cache = context.render_context.dicts[0].setdefault(self, {})
            template = cache.get(template_name)
            if template is None:
                engine = engines['handlebars']
                template = engine.get_template(template_name)
                cache[template_name] = template
        # Use the base.Template of a backends.django.Template.
        elif hasattr(template, 'template'):
            template = template.template
        values = {
            name: var.resolve(context)
            for name, var in self.extra_context.items()
        }
        if self.isolated_context:
            return template.render(context.new(values))
        with context.push(**values):
            return template.render(context)


@register.tag
def include_handlebars(parser, token):
    """
    Include a Handlebars template processed with the current context.
    """
    bits = token.contents.split()
    if len(bits) != 2:
        raise TemplateSyntaxError(
            "'include_handlebars' tag takes one argument: the name/id of "
            "the template to include.")
    return IncludeHandlebarsNode(*bits[1:])


@register.tag
def include_raw_handlebars(parser, token):
    """
    Performs a template include without parsing the context, just dumps the template in.
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("%r tag takes one argument: the name of the template to be included" % bits[0])

    template_name = bits[1]
    if template_name[0] in ('"', "'") and template_name[-1] == template_name[0]:
        template_name = template_name[1:-1]

    if DJANGO_VERSION >= (1, 8):
        engine = engines['handlebars']
        template, origin = engine.engine.find_template(template_name)
        source = origin.loader.get_contents(origin)
    else:
        source, _ = Loader().load_template_source(template_name)

    return TextNode(source)
