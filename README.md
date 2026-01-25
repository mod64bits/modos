# Sistema de Gestão de TI e Helpdesk (Django)

Este projeto é um sistema web desenvolvido em Django para gestão completa de departamentos de TI, focado em ambientes multi-empresa (multi-tenant). O sistema integra controle de acesso, inventário detalhado de hardware e gestão de chamados (Service Desk).

## 🚀 Funcionalidades Principais

### 1. Gestão Corporativa (App `accounts`)
* **Multi-tenant**: Estrutura preparada para gerir múltiplas empresas no mesmo banco de dados.
* **Hierarquia**: Empresa -> Setores -> Usuários.
* **Usuários Personalizados**: Login com vínculo obrigatório a uma Empresa e Setor.
* **Segurança**: Mixins de proteção para garantir que usuários só vejam dados da sua própria empresa.

### 2. Inventário de Ativos (App `equipamentos`)
* **Herança de Modelos**: 
    * `Equipamento` (Base): Serial, Marca, Modelo, Responsável.
    * `Computador` (Filho): Processador, RAM + Discos.
    * `Periferico` (Filho): Monitores, Teclados, Impressoras.
* **Gestão de Armazenamento**: Vínculo *One-to-Many* para múltiplos discos (SSD/HDD) por computador.
* **Rastreabilidade**: Periféricos podem ser vinculados ("plugados") a um computador específico ou ficarem livres no estoque.

### 3. Service Desk / Chamados (App `chamados`)
* **Tickets e O.S.**: Abertura de chamados para manutenção corretiva, preventiva ou requisições.
* **Integração**: Histórico de manutenção visível diretamente na tela do equipamento.
* **Fluxo de Trabalho**:
    * Atribuição de técnicos (apenas usuários `Staff`).
    * Log automático de transferência de técnicos (Auditoria).
    * Mudança automática de status (Aberto -> Em Atendimento).
    * Categorização por tipo de serviço (Hardware, Software, Rede).

## 🛠️ Instalação e Configuração

### Pré-requisitos
* Python 3.8+
* Django 4.0+
* `django-localflavor` (Opcional, para validação de CNPJ)

### Passo a Passo

1.  **Clonar e Instalar Dependências**
    ```bash
    pip install django django-stubs
    ```

2.  **Configuração Inicial**
    No arquivo `settings.py`, certifique-se de definir o modelo de usuário personalizado:
    ```python
    AUTH_USER_MODEL = 'accounts.Usuario'
    ```

3.  **Banco de Dados**
    ```bash
    python manage.py makemigrations accounts equipamentos chamados
    python manage.py migrate
    ```

4.  **Criar Superusuário**
    ```bash
    python manage.py createsuperuser
    ```

5.  **Rodar o Servidor**
    ```bash
    python manage.py runserver
    ```

## 📚 Estrutura do Admin

O painel administrativo foi altamente customizado para produtividade:

* **Empresas**: Criação de setores via *Inline* na mesma tela.
* **Computadores**: 
    * Adição de Discos e Periféricos na mesma tela.
    * Visualização do **Histórico de Chamados** do equipamento (Somente leitura).
* **Chamados**:
    * Filtros por status, prioridade e técnico.
    * Ação em massa para "Fechar Chamados".
    * Campo de auditoria automática para trocas de técnicos.

## 📝 Notas de Desenvolvimento

* **UUIDs**: Todos os modelos utilizam UUID como chave primária para maior segurança e facilidade em migrações de dados futuras.
* **Mixins**: Utilize o `EmpresaFilterMixin` em todas as Views para garantir o isolamento dos dados entre clientes.