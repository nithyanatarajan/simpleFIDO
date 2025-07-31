import {base64urlToBuffer, bufferToBase64url} from './utils.js';

export async function registerPasskey(username, account) {
  const apiBase = import.meta.env.VITE_API_BASE_URL;

    console.log(apiBase,'apiBase')
    // 1. Get publicKeyCredentialCreationOptions and challenge_token
    const res = await fetch(`${apiBase}/register/begin`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, org_id: 'orgA', account })
    });

    
    if (!res.ok) {
        throw new Error("Failed to get registration options");
    }
  

    const {publicKey, challenge_token} = await res.json();

    console.log(publicKey, challenge_token, 'response')

    sessionStorage.setItem('extended_auth_token', publicKey?.extensions?.extended_auth_token)

    // 2. Convert publicKey fields from base64 to ArrayBuffer
    publicKey.challenge = base64urlToBuffer(publicKey.challenge);
    publicKey.user.id = base64urlToBuffer(publicKey.user.id);

    if (publicKey.excludeCredentials) {
        publicKey.excludeCredentials = publicKey.excludeCredentials.map(cred => ({
            ...cred,
            id: base64urlToBuffer(cred.id)
        }));
    }

    publicKey.extensions = {
        ...publicKey.extensions,
        credProps: true
    }


    console.log('before calling webAuthn', publicKey)
    // 3. Call WebAuthn API
    const cred = await navigator.credentials.create({publicKey, });

    const isDiscoverable = publicKey.extensions.discoverable

    console.log('after calling webauthn', cred)
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

    console.log(attestation,'attestation')
    console.log(challenge_token,'challenge_token')

    // 5. Send back to /register/complete
    const verifyRes = await fetch(`${apiBase}/register/complete`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({attestation, challenge_token})
    });

    if(isDiscoverable){
        localStorage.setItem('enable_discoverable_login', true)
        document.getElementById('sign-in-with-passkey').style.visibility = 'visible'
    }
   

    if (!verifyRes.ok) {
        throw new Error("Registration failed");
    }

    return await verifyRes.json();
}
