from django.template import TextNode, Node, Variable, TemplateSyntaxError, Library
from django.template.loaders.app_directories import Loader
from ..template.loader import get_template

register = Library()


class IncludeHandlebarsNode(Node):
    def __init__(self, name):
        self.name = Variable(name)

    def render(self, context):
        name = self.name.resolve(context)
        template = get_template(name)

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
        raise TemplateSyntaxError, "%r tag takes one argument: the name of the template to be included" % bits[0]

    template_name = bits[1]
    if template_name[0] in ('"', "'") and template_name[-1] == template_name[0]:
        template_name = template_name[1:-1]

    source, path = Loader().load_template_source(template_name)

    return TextNode(source)
