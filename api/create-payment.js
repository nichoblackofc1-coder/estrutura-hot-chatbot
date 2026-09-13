export default async function handler(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Método não permitido' });
  }

  const { planId, customer, utm_source, utm_campaign, utm_medium, utm_content, utm_term } = req.body || {};

  const PLAN_CONFIG = {
    plano19: { title: 'VIP 30 Dias', unit_price: 1990 },
    plano27: { title: 'VIP 3 Meses', unit_price: 2790 },
    plano39: { title: 'VIP 1 Ano', unit_price: 3990 }
  };

  const plan = PLAN_CONFIG[planId] || PLAN_CONFIG.plano27;

  try {
    const response = await fetch('https://www.selectuspay.com.br/api/v1/create-payment', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer mp_live_d619e8f6acab3f3b7ea64e636c042943c67accf0cba07556',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
      },
      body: JSON.stringify({
        customer: customer || {
          name: 'Assinante VIP',
          email: 'assinante@vipclub.com',
          document: '39824317800',
          phone: '5511999999999'
        },
        payment_method: 'pix',
        items: [
          {
            title: plan.title,
            unit_price: plan.unit_price,
            quantity: 1
          }
        ],
        utm_source: utm_source || undefined,
        utm_campaign: utm_campaign || undefined,
        utm_medium: utm_medium || undefined,
        utm_content: utm_content || undefined,
        utm_term: utm_term || undefined
      })
    });

    const data = await response.json();
    return res.status(response.status || 200).json(data);
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}
