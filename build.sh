#!/bin/bash
# Build script otimizado para Render

echo "🔧 Iniciando build do Sistema de Banco de Horas..."

# Atualizar pip
echo "📦 Atualizando pip..."
pip install --upgrade pip setuptools wheel

# Instalar dependências
echo "📋 Instalando dependências..."
pip install -r requirements.txt

# Verificar se as dependências foram instaladas
echo "✅ Verificando instalação..."
python -c "import flask, sqlalchemy; print('Dependencies OK')"

# Inicializar banco (somente se DATABASE_URL estiver configurado)
if [ -n "$DATABASE_URL" ]; then
    echo "🗄️ Inicializando banco de dados..."
    python init_db.py
else
    echo "⚠️ DATABASE_URL não configurado - pulando inicialização do banco"
fi

echo "🎉 Build concluído com sucesso!"