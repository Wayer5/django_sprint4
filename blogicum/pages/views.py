from django.shortcuts import render
from django.views.generic import TemplateView


class About(TemplateView):

    template_name = 'pages/about.html'


class Rules(TemplateView):

    template_name = 'pages/rules.html'


def about(request):
    template_name = 'pages/about.html'
    return render(request, template_name)


def rules(request):
    template_name = 'pages/rules.html'
    return render(request, template_name)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def custom_server_error(request):
    return render(request, 'pages/500.html', status=500)


class HomePage(TemplateView):
    template_name = 'blog/index.html'


def csrf_failure_view(request, reason=""):
    return csrf_failure(request, reason)
