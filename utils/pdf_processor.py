import PyPDF2
import pdfplumber
import re
from decimal import Decimal
import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

def processar_pdf(filepath, tipo):
    """
    Processa PDF e extrai valores baseado no tipo
    Agora com suporte OCR para PDFs digitalizados
    """
    try:
        print(f"🔍 Processando {tipo}: {filepath}")
        
        if tipo == 'pedagio':
            return extrair_valor_pedagio(filepath)
        elif tipo == 'alimentacao':
            return extrair_valor_alimentacao(filepath)
        elif tipo == 'hospedagem':
            return extrair_valor_hospedagem(filepath)
        else:
            return 0
    except Exception as e:
        print(f"❌ Erro ao processar PDF {filepath}: {e}")
        return 0

def extrair_texto_pdf_hibrido(filepath):
    """
    Extrai texto do PDF usando método híbrido:
    1. Primeiro tenta pdfplumber (PDFs com texto)
    2. Se falhar, usa OCR (PDFs digitalizados)
    """
    texto_completo = ""
    
    try:
        # Método 1: Tentar extrair texto normal
        print("📖 Tentando extração de texto normal...")
        with pdfplumber.open(filepath) as pdf:
            for i, page in enumerate(pdf.pages):
                texto_pagina = page.extract_text() or ""
                texto_completo += texto_pagina + "\n"
                print(f"📄 Página {i+1}: {len(texto_pagina)} caracteres")
        
        # Verificar se extraiu texto suficiente
        if len(texto_completo.strip()) > 50:
            print(f"✅ Texto extraído normalmente: {len(texto_completo)} caracteres")
            return texto_completo
        
        # Método 2: OCR para PDFs digitalizados
        print("🔍 Texto insuficiente, usando OCR...")
        return extrair_texto_com_ocr(filepath)
        
    except Exception as e:
        print(f"❌ Erro na extração híbrida: {e}")
        return ""

def extrair_texto_com_ocr(filepath):
    """
    Extrai texto usando OCR (Tesseract) para PDFs digitalizados
    """
    try:
        print("📷 Convertendo PDF para imagens...")
        
        # Converter PDF para imagens
        images = convert_from_path(filepath, dpi=300, first_page=1, last_page=3)
        print(f"🖼️ Convertidas {len(images)} páginas")
        
        texto_completo = ""
        
        for i, image in enumerate(images):
            print(f"🔤 Executando OCR na página {i+1}...")
            
            # Configurar Tesseract para português
            custom_config = r'--oem 3 --psm 6 -l por'
            
            # Extrair texto com OCR
            texto_pagina = pytesseract.image_to_string(image, config=custom_config)
            texto_completo += texto_pagina + "\n"
            
            print(f"📝 Página {i+1} OCR: {len(texto_pagina)} caracteres")
        
        print(f"✅ OCR concluído: {len(texto_completo)} caracteres total")
        return texto_completo
        
    except Exception as e:
        print(f"❌ Erro no OCR: {e}")
        return ""

def extrair_valor_pedagio(filepath):
    """
    Extrai valor total de pedágios do Conectcar
    """
    try:
        texto = extrair_texto_pdf_hibrido(filepath)
        
        if not texto:
            print("❌ Nenhum texto extraído do PDF")
            return 0
        
        print(f"🔍 Amostra do texto: {texto[:300]}...")
        
        # Padrões para Conectcar
        padroes_pedagio = [
            r'TOTAL\s+(\d+[,.]\d{2})',           # TOTAL 22,00
            r'Total.*?R?\$?\s*(\d+[,.]\d{2})',   # Total R$ 22,00
            r'Valor.*?total.*?(\d+[,.]\d{2})',   # Valor total 22,00
        ]
        
        valores_encontrados = []
        
        for padrao in padroes_pedagio:
            matches = re.findall(padrao, texto, re.IGNORECASE | re.MULTILINE)
            if matches:
                print(f"🎯 Padrão '{padrao}' encontrou: {matches}")
                for match in matches:
                    try:
                        valor_str = match.replace(',', '.')
                        valor = float(valor_str)
                        if valor > 0:
                            valores_encontrados.append(valor)
                    except:
                        continue
        
        if valores_encontrados:
            valor_final = max(valores_encontrados)
            print(f"✅ Valor de pedágio extraído: R$ {valor_final:.2f}")
            return valor_final
        
        print("❌ Nenhum valor de pedágio encontrado")
        return 0
        
    except Exception as e:
        print(f"❌ Erro ao extrair valor de pedágio: {e}")
        return 0

def extrair_valor_alimentacao(filepath):
    """
    Extrai valor de nota fiscal eletrônica (NFC-e)
    CORRIGIDO: Procura especificamente pelo TOTAL da nota
    """
    try:
        texto = extrair_texto_pdf_hibrido(filepath)
        
        if not texto:
            print("❌ Nenhum texto extraído do PDF")
            return 0
        
        print(f"🔍 Amostra do texto: {texto[:300]}...")
        
        # Padrões ESPECÍFICOS para TOTAL da nota (em ordem de prioridade)
        padroes_total = [
            # Padrões mais específicos primeiro
            r'Total\s*:\s*R?\$?\s*(\d+[,.]\d{2})',            # Total: R$ 75,23
            r'Valor\s+total\s+R\$\s*(\d+[,.]\d{2})',         # Valor total R$ 75,23
            r'(?:^|\n)Total\s+R?\$?\s*(\d+[,.]\d{2})',       # Total 75,23 (início de linha)
            r'TOTAL\s*R?\$?\s*(\d+[,.]\d{2})',               # TOTAL R$ 75,23
            r'Vl\s+Total\s+(\d+[,.]\d{2})',                  # Vl Total 75,23
            
            # Para OCR com possíveis erros
            r'Total\s*[:\.]?\s*R?\s*\$?\s*(\d+[,.]\d{2})',   # Total : R $ 75,23
            r'(?:fotal|Fotal|total)\s*[:\.]?\s*R?\s*\$?\s*(\d+[,.]\d{2})', # OCR pode ler "Total" como "fotal"
        ]
        
        # Primeiro: tentar padrões específicos de TOTAL
        for padrao in padroes_total:
            matches = re.findall(padrao, texto, re.IGNORECASE | re.MULTILINE)
            if matches:
                print(f"🎯 TOTAL encontrado com padrão '{padrao}': {matches}")
                try:
                    valor_str = matches[0].replace(',', '.')
                    valor = float(valor_str)
                    if valor > 0:
                        print(f"✅ Valor TOTAL de alimentação extraído: R$ {valor:.2f}")
                        return valor
                except:
                    continue
        
        print("⚠️ TOTAL específico não encontrado, procurando padrões gerais...")
        
        # Segundo: padrões mais gerais, mas filtrados
        padroes_gerais = [
            r'R\s*\$\s*(\d+[,.]\d{2})(?=\s*(?:\n|$))',       # R$ 75,23 no final da linha
            r'(\d{2,3}[,.]\d{2})(?=\s*(?:\n|$|reais?))',     # 75,23 seguido de fim de linha ou "reais"
        ]
        
        valores_encontrados = []
        
        for padrao in padroes_gerais:
            matches = re.findall(padrao, texto, re.IGNORECASE | re.MULTILINE)
            if matches:
                print(f"🔍 Padrão geral '{padrao}' encontrou: {matches}")
                for match in matches:
                    try:
                        valor_str = match.replace(',', '.')
                        valor = float(valor_str)
                        # Filtrar valores razoáveis para alimentação (evitar valores muito altos como códigos)
                        if 5.0 <= valor <= 500.0:
                            valores_encontrados.append(valor)
                    except:
                        continue
        
        if valores_encontrados:
            # Para notas fiscais, geralmente o total é um dos maiores valores
            # Mas vamos pegar valores únicos e mostrar opções
            valores_unicos = list(set(valores_encontrados))
            valores_unicos.sort(reverse=True)
            
            print(f"💡 Valores candidatos encontrados: {valores_unicos}")
            
            # Pegar o valor mais provável (geralmente entre os maiores)
            valor_final = valores_unicos[0]
            print(f"✅ Valor de alimentação extraído: R$ {valor_final:.2f}")
            return valor_final
        
        print("❌ Nenhum valor de alimentação encontrado")
        return 0
        
    except Exception as e:
        print(f"❌ Erro ao extrair valor de alimentação: {e}")
        return 0

def extrair_valor_hospedagem(filepath):
    """
    Extrai valores de comprovantes de hospedagem
    """
    try:
        texto = extrair_texto_pdf_hibrido(filepath)
        
        if not texto:
            print("❌ Nenhum texto extraído do PDF")
            return 0
        
        print(f"🔍 Amostra do texto: {texto[:300]}...")
        
        # Padrões para hospedagem
        padrões_hospedagem = [
            r'Total.*?R\$\s*(\d+[,.]\d{2})',
            r'Valor.*?R\$\s*(\d+[,.]\d{2})',
            r'TOTAL.*?(\d+[,.]\d{2})',
            r'Subtotal.*?(\d+[,.]\d{2})',
            r'(\d+[,.]\d{2})\s*(?:reais?|R\$)',
        ]
        
        valores_encontrados = []
        
        for padrao in padrões_hospedagem:
            matches = re.findall(padrao, texto, re.IGNORECASE)
            if matches:
                print(f"🎯 Padrão '{padrao}' encontrou: {matches}")
                for match in matches:
                    try:
                        valor_str = match.replace(',', '.')
                        valor = float(valor_str)
                        if valor > 0:
                            valores_encontrados.append(valor)
                    except:
                        continue
        
        if valores_encontrados:
            valor_final = max(valores_encontrados)
            print(f"✅ Valor de hospedagem extraído: R$ {valor_final:.2f}")
            return valor_final
        
        print("❌ Nenhum valor de hospedagem encontrado")
        return 0
        
    except Exception as e:
        print(f"❌ Erro ao extrair valor de hospedagem: {e}")
        return 0

def debug_pdf_content(filepath):
    """
    Função para debugar o conteúdo completo de um PDF
    """
    try:
        print(f"\n🔍 === DEBUG COMPLETO: {filepath} ===")
        texto_completo = extrair_texto_pdf_hibrido(filepath)
        print("TEXTO COMPLETO:")
        print(texto_completo)
        print("=== FIM DEBUG ===\n")
    except Exception as e:
        print(f"❌ Erro ao debugar PDF: {e}")
