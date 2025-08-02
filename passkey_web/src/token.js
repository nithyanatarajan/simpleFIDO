export async function getAccountToken(username, password, accountId) {
  const idpBase = import.meta.env.VITE_IDP_BASE_URL;
  const res = await fetch(`${idpBase}/token/generate`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, password, account_id: accountId}),
  });

  if (!res.ok) {
    const {detail} = await res.json();
    throw new Error(`Token request failed: ${detail}`);
  }

  const {token} = await res.json();
  return token;
}
