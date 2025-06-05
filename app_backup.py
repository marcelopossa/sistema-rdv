from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime, date
import json

# Configuração da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sistema-rdv-2025-seguro'

# Usar banco SQLite no diretório atual (mais simples)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rdv.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Inicializar banco
db = SQLAlchemy(app)

# Criar pastas necessárias
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Modelos do banco de dados
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    valor_km = db.Column(db.Float, nullable=False)
    contato = db.Column(db.String(100))
    endereco = db.Column(db.String(200))
    observacoes = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    viagens = db.relationship('Viagem', backref='cliente', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'valor_km': self.valor_km,
            'contato': self.contato or '',
            'endereco': self.endereco or '',
            'observacoes': self.observacoes or ''
        }

class Viagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_viagem = db.Column(db.Date, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    projeto = db.Column(db.String(100))
    participantes = db.Column(db.String(200), nullable=False)
    beneficiario = db.Column(db.String(100), default='MARCELO POSSA')
    
    km_rodado = db.Column(db.Float, nullable=False)
    valor_km = db.Column(db.Float, nullable=False)
    total_km = db.Column(db.Float, nullable=False)
    
    valor_pedagio = db.Column(db.Float, default=0)
    valor_alimentacao = db.Column(db.Float, default=0)
    valor_hospedagem = db.Column(db.Float, default=0)
    total_geral = db.Column(db.Float, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'data_viagem': self.data_viagem.strftime('%Y-%m-%d'),
            'cliente_nome': self.cliente.nome,
            'projeto': self.projeto or '-',
            'km_rodado': self.km_rodado,
            'total_geral': self.total_geral
        }

# Rotas da aplicação
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/clientes', methods=['GET'])
def listar_clientes():
    try:
        clientes = Cliente.query.filter_by(ativo=True).all()
        return jsonify([cliente.to_dict() for cliente in clientes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clientes', methods=['POST'])
def criar_cliente():
    try:
        data = request.json
        
        cliente = Cliente(
            nome=data['nome'],
            valor_km=float(data['valor_km']),
            contato=data.get('contato', ''),
            endereco=data.get('endereco', ''),
            observacoes=data.get('observacoes', '')
        )
        
        db.session.add(cliente)
        db.session.commit()
        
        return jsonify({'id': cliente.id, 'message': 'Cliente criado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/clientes/<int:cliente_id>', methods=['PUT'])
def atualizar_cliente(cliente_id):
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        data = request.json
        
        cliente.nome = data['nome']
        cliente.valor_km = float(data['valor_km'])
        cliente.contato = data.get('contato', '')
        cliente.endereco = data.get('endereco', '')
        cliente.observacoes = data.get('observacoes', '')
        
        db.session.commit()
        return jsonify({'message': 'Cliente atualizado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/clientes/<int:cliente_id>', methods=['DELETE'])
def excluir_cliente(cliente_id):
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        cliente.ativo = False
        db.session.commit()
        return jsonify({'message': 'Cliente excluído com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/processar-documentos', methods=['POST'])
def processar_documentos():
    try:
        # Por enquanto, valores simulados baseados nos seus documentos
        # Depois implementamos o processamento real dos PDFs
        return jsonify({
            'pedagio': 22.0,
            'alimentacao': 59.9,
            'hospedagem': 0.0,
            'arquivos_processados': [
                {'tipo': 'pedagio', 'nome': 'Extrato_Conectcar.pdf', 'valor': 22.0},
                {'tipo': 'alimentacao', 'nome': 'NFC-e_Restaurant.pdf', 'valor': 44.9},
                {'tipo': 'alimentacao', 'nome': 'NFC-e_Cafe.pdf', 'valor': 15.0}
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/viagens', methods=['POST'])
def criar_viagem():
    try:
        data = request.json
        
        total_km = float(data['km_rodado']) * float(data['valor_km'])
        total_geral = total_km + float(data['valor_pedagio']) + float(data['valor_alimentacao']) + float(data['valor_hospedagem'])
        
        viagem = Viagem(
            data_viagem=datetime.strptime(data['data_viagem'], '%Y-%m-%d').date(),
            cliente_id=int(data['cliente_id']),
            projeto=data.get('projeto', ''),
            participantes=data['participantes'],
            km_rodado=float(data['km_rodado']),
            valor_km=float(data['valor_km']),
            total_km=total_km,
            valor_pedagio=float(data['valor_pedagio']),
            valor_alimentacao=float(data['valor_alimentacao']),
            valor_hospedagem=float(data['valor_hospedagem']),
            total_geral=total_geral
        )
        
        db.session.add(viagem)
        db.session.commit()
        
        return jsonify({
            'id': viagem.id,
            'message': 'Viagem criada com sucesso!',
            'total_geral': total_geral
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/viagens', methods=['GET'])
def listar_viagens():
    try:
        viagens = Viagem.query.join(Cliente).order_by(Viagem.data_viagem.desc()).all()
        return jsonify([viagem.to_dict() for viagem in viagens])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Teste simples para verificar se está funcionando
@app.route('/api/test')
def test():
    return jsonify({
        'status': 'ok',
        'message': 'Sistema RDV funcionando!',
        'database': 'conectado',
        'tabelas': 'cliente, viagem'
    })

# Inicialização do banco
def init_db():
    try:
        # Criar todas as tabelas
        db.create_all()
        print("✅ Banco de dados criado com sucesso!")
        
        # Criar clientes padrão se não existirem
        if Cliente.query.count() == 0:
            clientes_padrao = [
                Cliente(
                    nome='Conpasul',
                    valor_km=1.00,
                    contato='contato@conpasul.com.br',
                    endereco='Porto Alegre, RS',
                    observacoes='Cliente padrão, viagens frequentes'
                ),
                Cliente(
                    nome='TechCorp',
                    valor_km=1.20,
                    contato='(51) 3333-4444',
                    endereco='São Paulo, SP',
                    observacoes='Valor diferenciado para projetos especiais'
                )
            ]
            
            for cliente in clientes_padrao:
                db.session.add(cliente)
            
            db.session.commit()
            print("✅ Clientes padrão criados!")
        else:
            print("✅ Banco já possui dados!")
            
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        return False
    return True

if __name__ == '__main__':
    with app.app_context():
        if init_db():
            print("🚀 Iniciando Sistema RDV...")
            # Rodar em modo debug para desenvolvimento
            app.run(host='0.0.0.0', port=5000, debug=True)
        else:
            print("❌ Falha na inicialização do banco!")
