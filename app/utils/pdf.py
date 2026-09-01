from flask import make_response
import re

def render_pdf_response(html_content: str, filename: str, fallback_endpoint: str = None, fallback_args: dict = None):
    """
    Gera um PDF usando WeasyPrint quando disponível.
    Se o WeasyPrint/GTK3 não estiver instalado no sistema, renderiza a página HTML
    limpa e auto-contida, disparando automaticamente a caixa de diálogo de impressão nativa (window.print()).
    """
    try:
        from weasyprint import HTML
        pdf_bytes = HTML(string=html_content).write_pdf()
        
        response = make_response(pdf_bytes)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f"inline; filename={filename}"
        return response
    except Exception:
        # Fallback de alta fidelidade: entrega o HTML limpo com acionamento automático de impressão nativa
        enhanced_html = html_content
        if "window.print()" not in enhanced_html:
            script = "\n<script>\n  window.addEventListener('DOMContentLoaded', () => {\n    setTimeout(() => { window.print(); }, 300);\n  });\n</script>\n"
            if "</body>" in enhanced_html:
                enhanced_html = enhanced_html.replace("</body>", f"{script}</body>", 1)
            else:
                enhanced_html += script

        response = make_response(enhanced_html)
        response.headers["Content-Type"] = "text/html; charset=utf-8"
        return response
