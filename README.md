# Automation Desk - Ticket Desk Automation

Este é um projeto Python que automatiza a integração com a API do Desk.ms para obter e gerenciar categorias e subcategorias de tickets. Ele utiliza um bot do Telegram para enviar e receber informações relacionadas ao processo de ticket.

## Funcionalidades

- **Autenticação automática**: O projeto faz a autenticação com a API Desk.ms e obtém um token que é utilizado nas requisições subsequentes.
- **Lista de Subcategorias**: Obtém uma lista de subcategorias de tickets via API do Desk.ms.
- **Gerenciamento de Token**: Verifica e atualiza automaticamente o token de autenticação quando expirar.
- **Integração com Telegram**: O bot envia e recebe informações via Telegram, como notificações de status.

## Pré-requisitos

- Python 3.8 ou superior
- `poetry` para gerenciamento de dependências
- Conta no **Desk.ms** e um token de autenticação para configurar as credenciais
- Token do Telegram para o bot

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/automation-python-ticket-desk.git
cd automation-python-ticket-desk
