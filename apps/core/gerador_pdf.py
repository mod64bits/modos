import os
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from xhtml2pdf import pisa

def link_callback(uri, rel):
    """
    Garante que o xhtml2pdf consiga encontrar imagens se as usar no HTML do PDF.
    """
    if uri.startswith(settings.STATIC_URL):
        return os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    elif uri.startswith(settings.MEDIA_URL):
        return os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    return uri

def render_to_pdf(template_src, context_dict={}):
    """
    Recebe um template HTML e dados de contexto, retornando o binário de um PDF.
    """
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    
    # Gera o PDF preservando os acentos em UTF-8
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
    
    if not pdf.err:
        return result.getvalue()
    return None