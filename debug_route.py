@app.route('/api/processar-documentos', methods=['POST'])
def processar_documentos():
    try:
        print("🚀 Iniciando processamento de documentos...")
        print(f"📋 Request files: {list(request.files.keys())}")
        print(f"📋 Request form: {list(request.form.keys())}")
        
        resultados = {
            'pedagio': 0,
            'alimentacao': 0,
            'hospedagem': 0,
            'arquivos_processados': []
        }
        
        # Debug todos os arquivos recebidos
        for field_name, file_obj in request.files.items():
            print(f"📁 Campo '{field_name}': {file_obj.filename}")
        
        # Processar cada tipo de arquivo com nomes corretos
        tipos_campos = {
            'pedagio': 'pedagioFile',
            'alimentacao': 'alimentacaoFiles', 
            'hospedagem': 'hospedagemFiles'
        }
        
        for tipo, field_name in tipos_campos.items():
            arquivos = request.files.getlist(field_name)
            print(f"📁 Processando {len(arquivos)} arquivo(s) de {tipo} (campo: {field_name})")
            
            for arquivo in arquivos:
                if arquivo.filename:
                    try:
                        # Salvar arquivo
                        filename = secure_filename(arquivo.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                        filename = timestamp + filename
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        arquivo.save(filepath)
                        
                        print(f"�� Arquivo salvo: {filepath}")
                        
                        # Processar PDF
                        valor_extraido = processar_pdf(filepath, tipo)
                        resultados[tipo] += valor_extraido
                        
                        resultados['arquivos_processados'].append({
                            'tipo': tipo,
                            'nome': arquivo.filename,
                            'valor': valor_extraido
                        })
                        
                        print(f"✅ {arquivo.filename}: R$ {valor_extraido:.2f}")
                        
                    except Exception as e:
                        print(f"❌ Erro ao processar {arquivo.filename}: {e}")
                        resultados['arquivos_processados'].append({
                            'tipo': tipo,
                            'nome': arquivo.filename,
                            'valor': 0,
                            'erro': str(e)
                        })
        
        print(f"🎉 Processamento concluído: {resultados}")
        return jsonify(resultados)
        
    except Exception as e:
        print(f"❌ Erro geral no processamento: {e}")
        return jsonify({'error': str(e)}), 500
