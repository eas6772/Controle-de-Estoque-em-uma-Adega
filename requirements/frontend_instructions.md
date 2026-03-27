# Diretrizes de Frontend: Flask + Jinja2 + Bootstrap

Este projeto utiliza o motor de templates **Jinja2** para renderização no lado do servidor e **Bootstrap 5** para a interface.

## 1. Estrutura de Templates (Jinja2)
- **Base Template:** Todos os arquivos devem estender `base.html`.
- **Blocos Padrão:** 
    - `{% block title %}`: Para títulos dinâmicos de página.
    - `{% block content %}`: Para o corpo principal.
    - `{% block scripts %}`: Para scripts específicos da página (abaixo do bundle do Bootstrap).
- **Componentes:** Use `{% include 'partials/_nav.html' %}` para componentes reutilizáveis.
- **Macros:** Crie macros em `templates/macros.html` para formulários e botões repetitivos.

## 2. Estilização (Bootstrap 5)
- **Classes Nativas:** Priorize classes utilitárias do Bootstrap (ex: `d-flex`, `mt-3`, `text-center`) em vez de CSS personalizado.
- **Responsividade:** Use o sistema de grid (`container`, `row`, `col-md-X`) rigorosamente.
- **Customização:** Se necessário CSS extra, use um arquivo `static/css/style.css` e vincule-o no `base.html`.

## 3. Convenções de Código
- **URLs Dinâmicas:** Nunca use caminhos estáticos. Use sempre `{{ url_for('static', filename='css/style.css') }}` ou `{{ url_for('blueprint.route') }}`.
- **Filtros:** Use filtros do Jinja2 para formatar dados (ex: `{{ data | datetimeformat }}`).
- **Mensagens Flash:** Implemente o suporte a `get_flashed_messages()` usando os alertas do Bootstrap (`alert-dismissible`).

## 4. Integração com Backend
- **Formulários:** Sempre inclua campos ocultos se usar CSRF Protection.
- **Validação:** Exiba erros de validação abaixo dos inputs usando a classe `.invalid-feedback` do Bootstrap, ativada pela classe `.is-invalid` no input.

## 5. Requisitos Específicos do Plano
- **Dashboard:** Cards de resumo para Total em estoque, Alertas de validade e Vendas do dia.
- **Gestão:** Botão de "Entrada Rápida" para produtos de alta rotatividade.
- **Feedback:** Alertas visuais para produtos vencendo em < 30 dias.
