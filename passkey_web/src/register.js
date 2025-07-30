import {base64urlToBuffer, bufferToBase64url} from './utils.js';

export async function registerPasskey(username) {
  const apiBase = import.meta.env.VITE_API_BASE_URL;

  // 1. Get publicKeyCredentialCreationOptions and challenge_token
  const res = await fetch(`${apiBase}/register/begin`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username})
  });

  if (!res.ok) {
    throw new Error('Failed to get registration options');
  }

  const {publicKey, challenge_token} = await res.json();

  // 2. Convert publicKey fields from base64 to ArrayBuffer
  publicKey.challenge = base64urlToBuffer(publicKey.challenge);
  publicKey.user.id = base64urlToBuffer(publicKey.user.id);

  if (publicKey.excludeCredentials) {
    publicKey.excludeCredentials = publicKey.excludeCredentials.map(cred => ({
      ...cred,
      id: base64urlToBuffer(cred.id)
    }));
  }

  // 3. Call WebAuthn API
  const cred = await navigator.credentials.create({publicKey});

  // 4. Convert credential response to JSON-safe structure
  const attestation = {
    id: cred.id,
    type: cred.type,
    rawId: bufferToBase64url(cred.rawId),
    response: {
      attestationObject: bufferToBase64url(cred.response.attestationObject),
      clientDataJSON: bufferToBase64url(cred.response.clientDataJSON)
    }
  };

  // 5. Send back to /register/complete
  const verifyRes = await fetch(`${apiBase}/register/complete`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({attestation, challenge_token})
  });

  if (!verifyRes.ok) {
    throw new Error('Registration failed');
  }

  return await verifyRes.json();
}
