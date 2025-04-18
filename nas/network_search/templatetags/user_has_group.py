from django import template


register = template.Library()


@register.filter(name='has_group')
def has_group(user, groupname):
    return user.groups.filter(name__contains=groupname)
