// register.js
import {base64urlToBuffer, withExtensions, prepareRegistrationAttestationPayload} from './utils.js';

export async function registerPasskey(username, accountToken) {
  const apiBase = import.meta.env.VITE_API_BASE_URL;

  // 1. Begin registration with RP backend
  const res = await fetch(`${apiBase}/register/begin`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username}),
  });

  if (!res.ok) {
    const {detail} = await res.json();
    throw new Error(`Registration begin failed: ${detail}`);
  }

  const {publicKey, challenge_token} = await res.json();

  // 2. Convert challenge and user.id
  publicKey.challenge = base64urlToBuffer(publicKey.challenge);
  publicKey.user.id = base64urlToBuffer(publicKey.user.id);

  if (publicKey.excludeCredentials) {
    publicKey.excludeCredentials = publicKey.excludeCredentials.map((cred) => ({
      ...cred,
      id: base64urlToBuffer(cred.id),
    }));
  }

  // 3. Inject extensions
  const publicKeyWithExtensions = withExtensions(publicKey, accountToken);

  // 4. Call WebAuthn API
  const credential = await navigator.credentials.create({
    publicKey: publicKeyWithExtensions,
  });

  if (!credential) {
    throw new Error('Credential creation failed or was cancelled.');
  }

  // 5. Prepare attestation object
  const attestation = prepareRegistrationAttestationPayload(credential);

  // ✅ 6. Call RP backend to complete registration
  const finishRes = await fetch(`${apiBase}/register/complete`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accountToken}`
    },
    body: JSON.stringify({attestation, challenge_token}),
  });

  if (!finishRes.ok) {
    const {detail} = await finishRes.json();
    throw new Error(`Registration complete failed: ${detail}`);
  }

  return await finishRes.json(); // if needed
}
