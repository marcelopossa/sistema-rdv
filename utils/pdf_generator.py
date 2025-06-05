from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from PyPDF2 import PdfWriter, PdfReader
import os
from datetime import datetime
import glob

def gerar_pdf_completo(viagem):
    """
    Gera PDF completo: Relatório + Anexos dos comprovantes
    """
    try:
        print(f"📄 Gerando PDF completo para viagem ID: {viagem.id}")
        
        # Gerar relatório principal
        relatorio_path = gerar_relatorio_pdf(viagem)
        
        if not relatorio_path:
            return None, None
        
        # Compilar PDF final com anexos
        pdf_final_path = compilar_pdf_com_anexos(viagem, relatorio_path)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"RDV_Completo_{viagem.cliente.nome}_{viagem.data_viagem.strftime('%Y%m%d')}_{timestamp}.pdf"
        
        return pdf_final_path, filename
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF completo: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def gerar_relatorio_pdf(viagem):
    """
    Gera apenas o relatório em PDF
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"relatorio_rdv_{timestamp}.pdf"
        filepath = os.path.join('static/uploads', filename)
        
        # Criar documento
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Estilo customizado
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Centralizado
        )
        
        # Título
        titulo = Paragraph("RELATÓRIO DE DESPESAS DE VIAGEM", titulo_style)
        story.append(titulo)
        story.append(Spacer(1, 20))
        
        # Informações do cabeçalho
        info_data = [
            ['Cliente:', viagem.cliente.nome, 'Data:', viagem.data_viagem.strftime('%d/%m/%Y')],
            ['Projeto:', viagem.projeto or '-', 'Beneficiário:', viagem.beneficiario],
            ['Participantes:', viagem.participantes, '', '']
        ]
        
        info_table = Table(info_data, colWidths=[80, 120, 80, 120])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Primeira coluna em negrito
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),  # Terceira coluna em negrito
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Tabela de despesas
        despesas_data = [
            ['Descrição', 'Quantidade', 'Valor Unitário', 'Total'],
            ['Quilometragem', f"{viagem.km_rodado:.0f} km", f"R$ {viagem.valor_km:.2f}".replace('.', ','), f"R$ {viagem.total_km:.2f}".replace('.', ',')],
        ]
        
        if viagem.valor_pedagio > 0:
            despesas_data.append(['Pedágio', '1', f"R$ {viagem.valor_pedagio:.2f}".replace('.', ','), f"R$ {viagem.valor_pedagio:.2f}".replace('.', ',')])
        
        if viagem.valor_alimentacao > 0:
            despesas_data.append(['Alimentação', '1', f"R$ {viagem.valor_alimentacao:.2f}".replace('.', ','), f"R$ {viagem.valor_alimentacao:.2f}".replace('.', ',')])
        
        if viagem.valor_hospedagem > 0:
            despesas_data.append(['Hospedagem', '1', f"R$ {viagem.valor_hospedagem:.2f}".replace('.', ','), f"R$ {viagem.valor_hospedagem:.2f}".replace('.', ',')])
        
        # Linha de total
        despesas_data.append(['', '', 'TOTAL GERAL:', f"R$ {viagem.total_geral:.2f}".replace('.', ',')])
        
        despesas_table = Table(despesas_data, colWidths=[120, 80, 100, 80])
        despesas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.yellow),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(despesas_table)
        story.append(Spacer(1, 40))
        
        # Informações de aprovação
        aprovacao_data = [
            ['Equipe:', '', 'Observações:', ''],
            ['', '', '', ''],
            ['Aprovação:', '', '', '']
        ]
        
        aprovacao_table = Table(aprovacao_data, colWidths=[80, 120, 80, 120])
        aprovacao_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(aprovacao_table)
        
        # Construir PDF
        doc.build(story)
        print(f"✅ Relatório PDF gerado: {filepath}")
        
        return filepath
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório PDF: {e}")
        return None

def compilar_pdf_com_anexos(viagem, relatorio_path):
    """
    Compila PDF final: Relatório + Anexos de comprovantes
    """
    try:
        # Criar PDF writer
        pdf_writer = PdfWriter()
        
        # Adicionar relatório principal
        with open(relatorio_path, 'rb') as relatorio_file:
            relatorio_reader = PdfReader(relatorio_file)
            for page in relatorio_reader.pages:
                pdf_writer.add_page(page)
        
        print("✅ Relatório principal adicionado")
        
        # Procurar e adicionar anexos na pasta uploads
        anexos_encontrados = 0
        upload_folder = 'static/uploads'
        
        # Buscar PDFs que podem ser anexos desta viagem
        data_str = viagem.data_viagem.strftime('%Y%m%d')
        
        # Padrões de arquivos da viagem atual
        padroes = [
            f"*{data_str}*",  # Arquivos com a data da viagem
            "*Extrato*",      # Extratos
            "*NFC*",          # Notas fiscais
            "*Digitalizado*", # PDFs digitalizados
            "*Conectcar*",    # Conectcar
        ]
        
        arquivos_anexados = set()
        
        for padrao in padroes:
            arquivos = glob.glob(os.path.join(upload_folder, padrao + ".pdf"))
            
            for arquivo_path in arquivos:
                if arquivo_path not in arquivos_anexados and os.path.exists(arquivo_path):
                    try:
                        with open(arquivo_path, 'rb') as anexo_file:
                            anexo_reader = PdfReader(anexo_file)
                            for page in anexo_reader.pages:
                                pdf_writer.add_page(page)
                        
                        arquivos_anexados.add(arquivo_path)
                        anexos_encontrados += 1
                        print(f"✅ Anexo adicionado: {os.path.basename(arquivo_path)}")
                        
                    except Exception as e:
                        print(f"⚠️ Erro ao adicionar anexo {arquivo_path}: {e}")
        
        # Salvar PDF final
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_final = f"RDV_Completo_{viagem.cliente.nome}_{data_str}_{timestamp}.pdf"
        filepath_final = os.path.join(upload_folder, filename_final)
        
        with open(filepath_final, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        print(f"✅ PDF completo gerado: {filepath_final}")
        print(f"📊 Total de anexos incluídos: {anexos_encontrados}")
        
        # Limpar arquivo temporário do relatório
        if os.path.exists(relatorio_path):
            os.remove(relatorio_path)
        
        return filepath_final
        
    except Exception as e:
        print(f"❌ Erro ao compilar PDF com anexos: {e}")
        return None
