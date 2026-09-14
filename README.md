# Estrutura de Hot - Chatbot Interativo (WhatsApp Funnel)

Funil interativo de alta conversão simulando a interface nativa do WhatsApp Web/Mobile para venda de conteúdos VIP.

## 🚀 Funcionalidades Principais

- **Interface Realista do WhatsApp**:
  - Foto de perfil, status "online" e indicador de digitação ("digitando...").
  - Mensagens balão estilo WhatsApp com confirmação de leitura (`✓✓`).
  - Respostas rápidas profissionais no formato de chips com ícones vetoriais modernos.

- **Foto de Visualização Única (View-Once)**:
  - Exibição de tela cheia preenchida para mobile (`object-fit: cover`).
  - Timer regressivo visual de **2.5 segundos** com barra de progresso.
  - Bloqueio persistente: uma vez aberta, fica bloqueada mesmo se recarregar a página (com bypass `?reset=1` para testes de administração).

- **Popups e Cards de Planos (Estilo Privacy.com.br)**:
  - Fundo Obsidian Luxury escuro com gradientes coral/fogo (`#ff4c30` a `#ff1f52`).
  - **3 Planos Verticais**:
    1. **VIP 30 Dias** (R$ 14,90) - Com vídeo de prévia em looping.
    2. **VIP 3 Meses** (R$ 19,90 - Mais Vendido) - Com vídeo de prévia em looping e contorno neon.
    3. **VIP 1 Ano** (R$ 23,90 - Melhor Custo-Benefício) - Com vídeo de prévia em looping.
  - Botões de chamada para ação **"Assinar agora"**.

- **Modal Popup de Pagamento PIX**:
  - QR Code dinâmico em alta definição gerado automaticamente para cada plano.
  - Código "Pix Copia e Cola" com botão de cópia de um clique.
  - Indicador de status pulsante em tempo real.

## 🛠️ Como Executar Localmente

Você pode rodar qualquer servidor HTTP simples na pasta do projeto:

```bash
# Servidor multithread ultra rápido com cache otimizado
python server.py
```

Abra no navegador em:
```
http://localhost:8000
```
Para reiniciar o teste de visualização única:
```
http://localhost:8000/?reset=1
```
