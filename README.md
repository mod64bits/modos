# Sistema de Gestão de TI e Helpdesk (Django)

Este projeto é um sistema web desenvolvido em Django para gestão completa de departamentos de TI, focado em ambientes multi-empresa (multi-tenant). O sistema integra controlo de acesso, inventário detalhado de hardware e gestão de chamados (Service Desk).

## 🚀 Funcionalidades Principais

### 1. Gestão Corporativa (App `accounts`)
* **Multi-tenant**: Estrutura preparada para gerir múltiplas empresas na mesma base de dados.
* **Hierarquia**: Empresa -> Setores -> Utilizadores.
* **Utilizadores Personalizados**: Login com vínculo obrigatório a uma Empresa e Setor.
* **Segurança**: Mixins de proteção para garantir que os utilizadores só vejam dados da sua própria empresa.

### 2. Inventário de Ativos (App `equipamentos`)
* **Herança de Modelos**:
  * `Equipamento` (Base): Serial, Marca, Modelo, Responsável.
  * `Computador` (Filho): Processador, RAM + Discos.
  * `Periferico` (Filho): Monitores, Teclados, Impressoras.
* **Gestão de Armazenamento**: Vínculo *One-to-Many* para múltiplos discos (SSD/HDD) por computador.
* **Rastreabilidade**: Periféricos podem ser vinculados ("plugados") a um computador específico ou ficarem livres no stock.

### 3. Service Desk / Chamados (App `orders` / `chamados`)
* **Tickets e O.S.**: Abertura de chamados para manutenção corretiva, preventiva ou requisições.
* **Sistema de Comentários**: Interação contínua entre utilizador e técnico na página de detalhes da O.S., com suporte a upload de anexos (imagens/documentos). O formulário é bloqueado automaticamente quando o chamado é encerrado.
* **Fluxo de Trabalho**:
  * Atribuição de técnicos (apenas utilizadores `Staff`).
  * Registo automático de transferência de técnicos (Auditoria).
  * Mudança automática de status (Aberto -> Em Atendimento).
  * Categorização por tipo de serviço (Hardware, Software, Rede).

### 4. Dashboards e Gráficos (App `dashboard`)
* **Painel do Utilizador**: Visão consolidada de chamados em aberto, andamento e histórico. Inclui cancelamento seguro via Modal (protegido por CSRF).
* **Painel do Administrador/Técnico**:
  * Fila de espera de chamados (Não Atribuídos).
  * Opção rápida para o técnico "Puxar O.S." para si.
  * Gráficos dinâmicos (via Chart.js) exibindo o volume de chamados por status.
  * Filtros em tempo real na listagem.

### 5. Configurações Globais e Notificações (App `core`)
* **Design Dinâmico (Singleton)**: Alteração do Título do Sistema, texto de Rodapé e URL Base do sistema diretamente pelo Django Admin, refletindo instantaneamente em todo o site.
* **Servidor de E-mail (SMTP) no Admin**: Backend de e-mail customizado que lê as configurações (Host, Porta, Utilizador, Password, TLS) diretamente da base de dados. Permite trocar a conta de disparo sem alterar o código-fonte ou reiniciar o servidor.
* **Notificações Automáticas**: Disparo de e-mails em tempo real (utilizando Django Signals) para alertar solicitantes e técnicos sempre que um chamado for aberto ou atualizado.

---

## 🛠️ Instalação e Configuração

### Pré-requisitos
* Python 3.8+
* Django 4.0+
* `django-localflavor` (Opcional, para validação de CNPJ)
* `django-tailwind` (Para a renderização do frontend)

### Passo a Passo

1. **Clonar e Instalar Dependências**
   ```bash
   pip install django django-stubs django-tailwind