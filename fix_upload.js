// Função corrigida para upload
async function processarDocumentos() {
    console.log('🚀 Iniciando processamento...');
    
    const pedagioFiles = document.getElementById('pedagioFile').files;
    const alimentacaoFiles = document.getElementById('alimentacaoFiles').files;
    const hospedagemFiles = document.getElementById('hospedagemFiles').files;

    console.log('📁 Arquivos encontrados:');
    console.log('- Pedágio:', pedagioFiles.length);
    console.log('- Alimentação:', alimentacaoFiles.length);
    console.log('- Hospedagem:', hospedagemFiles.length);

    if (pedagioFiles.length === 0 && alimentacaoFiles.length === 0 && hospedagemFiles.length === 0) {
        showAlert('Por favor, selecione pelo menos um documento para processar.', 'error');
        return;
    }

    // Criar FormData corretamente
    const formData = new FormData();
    
    // Adicionar arquivos com nomes corretos
    Array.from(pedagioFiles).forEach(file => {
        formData.append('pedagioFile', file);
        console.log('✅ Adicionado pedágio:', file.name);
    });
    
    Array.from(alimentacaoFiles).forEach(file => {
        formData.append('alimentacaoFiles', file);
        console.log('✅ Adicionado alimentação:', file.name);
    });
    
    Array.from(hospedagemFiles).forEach(file => {
        formData.append('hospedagemFiles', file);
        console.log('✅ Adicionado hospedagem:', file.name);
    });

    try {
        console.log('📡 Enviando para servidor...');
        
        const response = await fetch('/api/processar-documentos', {
            method: 'POST',
            body: formData
            // NÃO definir Content-Type - deixar o browser fazer
        });
        
        const result = await response.json();
        console.log('📊 Resposta:', result);
        
        if (response.ok) {
            document.getElementById('valorPedagio').value = result.pedagio.toFixed(2);
            document.getElementById('valorAlimentacao').value = result.alimentacao.toFixed(2);
            document.getElementById('valorHospedagem').value = result.hospedagem.toFixed(2);
            
            showAlert('✅ Documentos processados com sucesso!', 'success');
            atualizarResumo();
        } else {
            showAlert(`Erro: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('❌ Erro:', error);
        showAlert('Erro ao processar documentos: ' + error.message, 'error');
    }
}
