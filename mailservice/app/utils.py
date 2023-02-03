from django.template import (
    Template, 
    Context
)


def render_content_template(content, ctx):
    context = Context(ctx)
    content_template = Template(content)
    rendered_content = content_template.render(context)
    return rendered_content