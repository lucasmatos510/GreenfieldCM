# 🕒 Sistema de Banco de Horas

![Flask](https://img.shields.io/badge/Flask-2.3.3-blue?style=for-the-badge&logo=flask)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?style=for-the-badge&logo=bootstrap)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=for-the-badge&logo=sqlite)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=for-the-badge)

Sistema completo e moderno para gestão automatizada de banco de horas com interface **mobile-first**, dashboard interativo e relatórios avançados.

## � Screenshots

| Desktop Dashboard | Mobile Interface | Relatórios |
|-------------------|------------------|------------|
| ![Dashboard](https://via.placeholder.com/300x200?text=Dashboard+Desktop) | ![Mobile](https://via.placeholder.com/300x200?text=Mobile+Interface) | ![Reports](https://via.placeholder.com/300x200?text=Advanced+Reports) |

## �🚀 Funcionalidades Principais

### 📊 Dashboard Interativo & Otimizado
- ✅ **19 erros corrigidos** e otimizado completamente
- 🎯 Visão geral das horas trabalhadas em tempo real
- 📈 Estatísticas dinâmicas e gráficos Chart.js
- 👥 Resumo de funcionários ativos
- 🎨 Interface **mobile-first** responsiva
- ⚡ Performance aprimorada com loading assíncrono

### 👥 Gestão Completa de Funcionários
- 📝 Cadastro completo com validação
- 🔗 Vinculação inteligente a cargos e funções
- ⚡ Controle de status (ativo/inativo)
- 📅 Histórico completo de admissão
- 🔍 Busca e filtros avançados

### 🏢 Organização Estrutural Corrigida
- 🎯 **Áreas de Atuação**: Tecnologia, RH, Vendas, etc. (JavaScript corrigido)
- 💼 **Cargos**: Vinculação inteligente às áreas
- 🎖️ **Funções**: Níveis hierárquicos (Junior, Pleno, Senior, etc.)
- ✅ **CRUD Completo**: Criar, editar, excluir com validação

### Registro de Horas
- Precisão em minutos
- Tipos de registro:
  - Normal
  - Hora Extra
  - Feriado
- Cálculo automático de duração
- Observações personalizadas

### 📊 Relatórios Avançados & Exportação Corrigida
- 📅 **Relatórios Diários**: Interface mobile-first com cards responsivos
- 📈 **Relatórios Mensais**: Consolidação corrigida e funcional
- 📋 **Relatórios Anuais**: Visão anual com filtros inteligentes
- 📤 **Exportação Excel**: Campos mapeados corretamente (`minutos_trabalhados → horas`, `area_atuacao → area`)
- 🎨 **Design Sofisticado**: Progressive disclosure e collapsible sections
- 📱 **FAB Button**: Ações rápidas flutuantes para mobile

### Recursos de Exportação
- Formato Excel (.xlsx)
- Dados organizados por:
  - Funcionário
  - Cargo
  - Área de atuação
  - Período
  - Tipo de registro
- Totalizadores automáticos

## 🛠️ Tecnologias Utilizadas

### 🔧 Backend Otimizado
- **Flask 2.3.3**: Framework web Python moderno
- **SQLAlchemy 2.0**: ORM avançado com relacionamentos corrigidos
- **Flask-Login**: Sistema de autenticação funcional (SECRET_KEY configurado)
- **SQLite**: Banco otimizado (configurável para PostgreSQL)
- **Werkzeug**: Segurança aprimorada

### 🎨 Frontend Mobile-First
- **HTML5**: Estrutura semântica moderna
- **CSS3 Custom**: Mobile-first + animações suaves
- **Bootstrap 5.3**: Framework responsivo otimizado
- **JavaScript ES6+**: Event listeners modernos corrigidos
- **Chart.js**: Gráficos dinâmicos responsivos
- **Font Awesome**: Ícones e micro-interactions
- **Progressive UX**: Disclosure patterns e collapsible sections

### 📤 Exportação & Utilitários
- **openpyxl**: Geração otimizada de Excel com campos corrigidos
- **python-dateutil**: Manipulação inteligente de datas
- **CSV Export**: Funcionalidade integrada nos resumos diários

## 🎉 **Melhorias Recentes (v2.0)**

### ✅ **Correções Implementadas:**
| Módulo | Status | Descrição |
|--------|--------|-----------|
| 📊 Dashboard | ✅ **19 erros corrigidos** | Performance, layout responsivo, cards interativos |
| 🔐 Login System | ✅ **Funcional** | Redirecionamento, sessões seguras, SECRET_KEY |
| 🏢 Áreas Gestão | ✅ **JavaScript corrigido** | Data attributes, event listeners, CRUD funcional |
| 📊 Resumos Diários | ✅ **Mobile-first redesign** | Cards responsivos, FAB buttons, progressive UX |
| 📤 Exportação | ✅ **Campos mapeados** | Excel organizado, filtros aplicados, estrutura correta |

### 🎨 **Design Mobile-First:**
- 📱 **Responsive Cards**: Timeline layout com avatars
- 🎯 **Progressive Disclosure**: Filtros colapsáveis inteligentes  
- 💫 **Animações CSS**: fadeInUp e micro-interactions
- 🔄 **FAB Actions**: Botão flutuante para ações rápidas
- 📊 **Stats Visualization**: Cards estatísticos responsivos
- 🌙 **Dark Mode**: Suporte opcional implementado

## 📦 Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação
1. Clone ou baixe o projeto
2. Navegue até o diretório do projeto
3. Ative o ambiente virtual (já configurado)
4. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Execução
```bash
python app.py
```

O sistema estará disponível em: `http://localhost:5000`

## 🗄️ Estrutura do Banco de Dados

### Tabelas Principais
- **areas_atuacao**: Áreas de trabalho da empresa
- **cargos**: Cargos vinculados às áreas
- **funcoes**: Funções/níveis hierárquicos
- **funcionarios**: Dados pessoais e profissionais
- **registros_horas**: Registros de tempo trabalhado

### Relacionamentos
- Funcionário → Cargo → Área de Atuação
- Funcionário → Função
- Funcionário → Múltiplos Registros de Horas

## 📊 Como Usar

### 1. Configuração Inicial
1. Acesse "Gerenciar Cargos"
2. Crie as áreas de atuação da empresa
3. Adicione cargos para cada área
4. Configure as funções/níveis

### 2. Cadastro de Funcionários
1. Acesse "Funcionários" → "Novo"
2. Preencha os dados pessoais
3. Selecione cargo e função
4. Salve o cadastro

### 3. Registro de Horas
1. Acesse "Registrar Horas"
2. Selecione o funcionário
3. Defina data e horários
4. Adicione observações se necessário
5. Salve o registro

### 4. Relatórios
1. Acesse "Relatórios"
2. Configure os filtros desejados
3. Visualize os dados na tela
4. Exporte para Excel se necessário

## 📈 Funcionalidades dos Relatórios

### Filtros Disponíveis
- Por funcionário específico
- Por período (data início/fim)
- Por tipo de registro
- Por área de atuação

### Tipos de Visualização
- **Detalhado**: Todos os registros individuais
- **Resumo**: Totalizações por funcionário
- **Mensal**: Agrupamento por mês

### Exportação Excel
- Planilhas organizadas
- Formatação profissional
- Fórmulas automáticas
- Gráficos inclusos

## 🔧 Personalização

### Configurações
- Chave secreta em `app.py`
- Configuração de banco em `app.py`
- Estilos CSS em `templates/base.html`

### Extensões Possíveis
- Autenticação de usuários
- Notificações por email
- API REST
- Integração com sistemas externos
- Backup automático

## 📱 Interface Responsiva

O sistema é totalmente responsivo, funcionando em:
- Desktops
- Tablets
- Smartphones

## 🆘 Solução de Problemas

### Erro de Banco de Dados
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Dependências Faltando
```bash
pip install -r requirements.txt
```

### Porta em Uso
Altere a porta em `app.py`:
```python
app.run(debug=True, port=5001)
```

## 📝 Licença

Este é um projeto de código aberto para uso interno da empresa.

## 👥 Suporte

Para suporte técnico ou dúvidas sobre o sistema, consulte a documentação interna ou entre em contato com a equipe de TI.

---

**Sistema de Banco de Horas v1.0**  
Desenvolvido para modernizar e automatizar o controle de horas trabalhadas.