import io
from flask import render_template, request, redirect, url_for, flash, send_file
from app.extensions import db
from app.models import Note
from app.utils.pdf import render_pdf_response

# Importa a blueprint definida no __init__.py do próprio módulo
from . import notes_bp


@notes_bp.route('/')
def list_notes():
    termo = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    
    query = Note.query
    
    # Filtro de Busca
    if termo:
        query = query.filter(
            (Note.titulo.ilike(f'%{termo}%')) | 
            (Note.conteudo.ilike(f'%{termo}%'))
        )
    
    # Paginação (6 notas por página)
    notes = query.order_by(Note.data_criacao.desc()).paginate(page=page, per_page=6, error_out=False)
    
    return render_template('notes/list.html', notes=notes, termo=termo)


@notes_bp.route('/novo', methods=['GET', 'POST'])
@notes_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@notes_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def form_note(id=None):
    note = Note.query.get_or_404(id) if id else Note()
    
    if request.method == 'POST':
        note.titulo = request.form.get('titulo')
        note.conteudo = request.form.get('conteudo')
        
        if not id:
            db.session.add(note)
            
        db.session.commit()
        flash('Anotação salva com sucesso!', 'success')
        return redirect(url_for('notes.list_notes'))

    return render_template('notes/form.html', note=note if id else None)


@notes_bp.route('/<int:id>/excluir', methods=['POST'])
def delete_note(id):
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    flash('Anotação excluída com sucesso!', 'success')
    return redirect(url_for('notes.list_notes'))


@notes_bp.route('/exportar-pdf')
def export_pdf():
    termo = request.args.get('q', '').strip()
    
    query = Note.query
    
    # Aplica o mesmo filtro de busca na hora de gerar o PDF
    if termo:
        query = query.filter(
            (Note.titulo.ilike(f'%{termo}%')) | 
            (Note.conteudo.ilike(f'%{termo}%'))
        )
        
    notes = query.order_by(Note.data_criacao.desc()).all()
    
    from datetime import datetime
    data_emissao = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    # Renderiza o template HTML para o PDF
    rendered_html = render_template('notes/pdf_template.html', notes=notes, termo=termo, data_emissao=data_emissao)
    
    return render_pdf_response(
        html_content=rendered_html,
        filename='anotacoes.pdf',
        fallback_endpoint='notes.list_notes'
    )