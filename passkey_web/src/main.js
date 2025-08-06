import {registerPasskey} from './register.js';
import {authenticateWithPasskey} from './auth.js';
import {generateTokens} from './token.js';
import {initiateExtensionSigning, validateExtensionSignature} from './extensions.js';

const AccountTokenRPSessionKey = 'accountTokenRP';
const AccountTokenExtnSessionKey = 'accountTokenExtn';
const UsernameSessionKey = 'username';

export async function handleGenerateToken(event) {
  event.preventDefault();
  const form = event.target;
  const username = form.username?.value.trim();
  const password = form.password?.value.trim();
  const accountId = form.account_id?.value.trim();
  const output = document.querySelector('#output');

  if (!username || !password || !accountId) {
    output.textContent = '⚠️ Username, password, and accountId are required.';
    return;
  }

  try {
    const {tokenRP, tokenExtn} = await generateTokens(username, password, accountId);
    sessionStorage.setItem(AccountTokenRPSessionKey, tokenRP);
    sessionStorage.setItem(AccountTokenExtnSessionKey, tokenExtn);
    sessionStorage.setItem(UsernameSessionKey, username);
    output.textContent = '✅ Tokens generated and stored in session.';
  } catch (err) {
    console.error(err);
    output.textContent = `❌ Error: ${err?.response?.data?.detail || err.message || 'Unknown error'}`;
  }
}

export async function handleRegister(event) {
  event.preventDefault();
  const form = event.target;
  const username = form.username?.value.trim() || sessionStorage.getItem(UsernameSessionKey);
  const accountToken = sessionStorage.getItem(AccountTokenRPSessionKey);
  const output = document.querySelector('#output');

  if (!username || !accountToken) {
    output.textContent = '⚠️ Username and accountToken required. Please generate token first.';
    return;
  }

  try {
    await registerPasskey(username, accountToken);
    output.textContent = '✅ Registered successfully.';
  } catch (err) {
    console.error(err);
    output.textContent = `❌ Error: ${err?.response?.data?.detail || err.message || 'Unknown error'}`;
  }
}

export async function handleAuthenticate(event) {
  event.preventDefault();
  const form = event.target;
  const username = form.username?.value.trim() || sessionStorage.getItem(UsernameSessionKey);
  const accountToken = sessionStorage.getItem(AccountTokenRPSessionKey);
  const output = document.querySelector('#output');

  if (!username || !accountToken) {
    output.textContent = '⚠️ Username and accountToken required. Please generate token first.';
    return;
  }

  try {
    await authenticateWithPasskey(username, accountToken);
    output.textContent = '✅ Authentication successful.';
  } catch (err) {
    console.error(err);
    output.textContent = `❌ Error: ${err?.response?.data?.detail || err.message || 'Unknown error'}`;
  }
}

export async function handleExtensionFlow(event) {
  event.preventDefault();
  const form = event.target;
  const username = form.username?.value.trim() || sessionStorage.getItem(UsernameSessionKey);
  const accountToken = sessionStorage.getItem(AccountTokenExtnSessionKey);
  const output = document.querySelector('#output');

  if (!username || !accountToken) {
    output.textContent = '⚠️ Username and accountToken required. Please generate token first.';
    return;
  }

  try {
    output.textContent = '🔄 Calling /extensions/prepare...\n';
    const prepareResponse = await initiateExtensionSigning(username, accountToken);
    output.textContent += `✅ Called /extensions/prepare response\n`;
    output.textContent += `${JSON.stringify(prepareResponse, null, 2)}\n`;


    output.textContent += '🔄 Calling /extensions/validate...\n';
    const validateResponse = await validateExtensionSignature(username, accountToken);
    output.textContent += `✅ Called /extensions/validate\n`;
    output.textContent += `${JSON.stringify(validateResponse, null, 2)}\n`;

  } catch (err) {
    console.error(err);
    output.textContent = `❌ Error: ${err?.response?.data?.detail || err.message || 'Unknown error'}`;
  }
}


const handlers = {
  generate: handleGenerateToken,
  register: handleRegister,
  authenticate: handleAuthenticate,
  extension: handleExtensionFlow
};

document.querySelectorAll('form[data-action]').forEach(form => {
  const action = form.dataset.action;
  const handler = handlers[action];

  if (handler) {
    form.addEventListener('submit', handler);
  } else {
    console.warn(`❌ No handler defined for action: ${action}`);
  }
});
