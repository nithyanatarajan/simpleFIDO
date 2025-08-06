export async function initiateExtensionSigning(username, accountToken) {
  const extnBase = import.meta.env.VITE_EXTN_BASE_URL;

  const res = await fetch(`${extnBase}/extensions/prepare`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accountToken}`,
    },
    body: JSON.stringify({username}),
  });

  if (!res.ok) {
    const {detail} = await res.json();
    throw new Error(`Extension prepare failed: ${detail}`);
  }

  return await res.json();
}


export async function validateExtensionSignature(username, accountToken) {
  const extnBase = import.meta.env.VITE_EXTN_BASE_URL;

  const res = await fetch(`${extnBase}/extensions/validate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accountToken}`,
    },
    body: JSON.stringify({username}),
  });

  if (!res.ok) {
    const {detail} = await res.json();
    throw new Error(`Extension validation failed: ${detail}`);
  }

  return await res.json();
}
