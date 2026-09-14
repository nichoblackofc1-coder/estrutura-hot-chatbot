module.exports = async function handler(req, res) {
  // Security Headers
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'SAMEORIGIN');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,POST');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Método não permitido' });
  }

  // Parse and validate body
  let body = req.body;
  if (typeof body === 'string') {
    try {
      body = JSON.parse(body);
    } catch (e) {
      return res.status(400).json({ error: 'Corpo da requisição inválido' });
    }
  }
  body = body || {};

  const { planId, utm_source, utm_campaign, utm_medium, utm_content, utm_term } = body;

  // Whitelist de planos válidos (Imutável do lado do servidor)
  const PLAN_WHITELIST = {
    plano9: { title: 'VIP 1 Mês Promocional', unit_price: 990 },
    plano19: { title: 'VIP 30 Dias', unit_price: 1490 },
    plano27: { title: 'VIP 3 Meses', unit_price: 1990 },
    plano39: { title: 'VIP 1 Ano', unit_price: 2390 }
  };

  const selectedPlan = PLAN_WHITELIST[planId];
  if (!selectedPlan) {
    return res.status(400).json({ error: 'Plano inválido ou inexistente' });
  }

  // Sanitização de parâmetros de rastreamento (limite de 100 chars e caracteres seguros)
  function sanitizeParam(val) {
    if (!val || typeof val !== 'string') return undefined;
    return val.replace(/[^a-zA-Z0-9_\-\.\:\s]/g, '').slice(0, 100);
  }

  // Recupera chave de API da variável de ambiente com fallback seguro
  const apiKey = process.env.SELECTUSPAY_API_KEY || 'mp_live_1c16778e07e94689e25571ed470e55c7e9c561742118ff8f';

  if (!apiKey) {
    return res.status(500).json({ error: 'Configuração do gateway pendente' });
  }

  try {
    const payload = {
      customer: {
        name: 'Cliente VIP',
        email: 'contato.vip@pagamento.com',
        document: '39824317800',
        phone: '5511999999999'
      },
      payment_method: 'pix',
      items: [
        {
          title: selectedPlan.title,
          unit_price: selectedPlan.unit_price,
          quantity: 1
        }
      ],
      utm_source: sanitizeParam(utm_source),
      utm_campaign: sanitizeParam(utm_campaign),
      utm_medium: sanitizeParam(utm_medium),
      utm_content: sanitizeParam(utm_content),
      utm_term: sanitizeParam(utm_term)
    };

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 9000);

    const response = await fetch('https://www.selectuspay.com.br/api/v1/create-payment', {
      method: 'POST',
      signal: controller.signal,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'User-Agent': 'HotChatbot-SecureClient/2.0'
      },
      body: JSON.stringify(payload)
    });

    clearTimeout(timeoutId);

    const data = await response.json();
    return res.status(response.status).json(data);
  } catch (error) {
    return res.status(502).json({ error: 'Comunicação indisponível no momento' });
  }
};
