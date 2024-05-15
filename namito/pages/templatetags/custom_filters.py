# from django import template
#
# from namito.pages.models import AdminPage
#
# register = template.Library()
#
#
# @register.simple_tag
# def get_admin_page_info():
#     admin_page, created = AdminPage.objects.get_or_create(pk=1)
#     if created:
#         admin_page.name = 'Namito'
#         admin_page.save()
#
#     return {
#         'logo': admin_page.logo.url if admin_page.logo else '',
#         'name': admin_page.name if admin_page.name else '',
#     }
