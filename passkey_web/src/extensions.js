import {base64urlToBuffer, prepareAuthenticationAssertionPayload} from "./utils.js";

async function initiateExtensionSigning(username, accountToken) {
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

  const {challenge} = await res.json();

  return {
    publicKey: {
      challenge: base64urlToBuffer(challenge),
    },
  };
}

async function validateExtensionSignature(username, accountToken, credential) {
  const extnBase = import.meta.env.VITE_EXTN_BASE_URL;

  const res = await fetch(`${extnBase}/extensions/validate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accountToken}`,
    },
    body: JSON.stringify({
      username,
      credential: prepareAuthenticationAssertionPayload(credential)
    }),
  });

  if (!res.ok) {
    const {detail} = await res.json();
    throw new Error(`Extension validation failed: ${detail}`);
  }

  return await res.json();
}

export async function runExtensionSigningFlow(username, accountToken) {
  // Step 1: Prepare challenge
  const {publicKey} = await initiateExtensionSigning(username, accountToken);

  // Step 2: Get signed credential from authenticator
  const credential = await navigator.credentials.get({publicKey});

  if (!credential) {
    throw new Error('No credential selected or user cancelled authentication.');
  }

  // Step 3: Validate assertion via extension server
  return await validateExtensionSignature(username, accountToken, credential);
}
