import {base64urlToBuffer, bufferToBase64url} from "./utils.js";

export async function loginWithPasskey(username) {
  const apiBase = import.meta.env.VITE_API_BASE_URL || window.location.origin;

  // 1. Begin authentication → get `publicKey` and `challenge_token`
  const beginRes = await fetch(`${apiBase}/authenticate/begin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username })
  });

  if (!beginRes.ok) throw new Error("Failed to begin authentication");

  const { publicKey, challenge_token } = await beginRes.json();

  // 2. Decode publicKey.challenge and allowCredentials[].id
  publicKey.challenge = base64urlToBuffer(publicKey.challenge);
  if (publicKey.allowCredentials) {
    publicKey.allowCredentials = publicKey.allowCredentials.map(cred => ({
      ...cred,
      id: base64urlToBuffer(cred.id)
    }));
  }

  // 3. Call WebAuthn API
  const cred = await navigator.credentials.get({ publicKey });

  // 4. Convert to JSON-safe structure
  const assertion = {
    id: cred.id,
    type: cred.type,
    rawId: bufferToBase64url(cred.rawId),
    response: {
      authenticatorData: bufferToBase64url(cred.response.authenticatorData),
      clientDataJSON: bufferToBase64url(cred.response.clientDataJSON),
      signature: bufferToBase64url(cred.response.signature),
      userHandle: cred.response.userHandle
        ? bufferToBase64url(cred.response.userHandle)
        : null
    }
  };

  // 5. Complete authentication
  const completeRes = await fetch(`${apiBase}/authenticate/complete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ assertion, challenge_token })
  });

  if (!completeRes.ok) throw new Error("Authentication failed");

  return await completeRes.json();
}
