import {registerPasskey} from './register.js';
import {authenticateWithPasskey} from './auth.js';
import {generateTokens} from './token.js';
import {runExtensionSigningFlow} from './extensions.js';

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
  if (username) {
    document.querySelectorAll('.username').forEach(el => {
      el.value = username;
    });
  }

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
    const result = await registerPasskey(username, accountToken);
    output.textContent = '✅ Registered successfully.';
    output.textContent += `\n${JSON.stringify(result, null, 2)}\n`;
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
    const result = await authenticateWithPasskey(username, accountToken);
    output.textContent = '✅ Authentication successful.';
    output.textContent += `\n${JSON.stringify(result, null, 2)}\n`;
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
    output.textContent = 'Extension signing in progress...\n';
    const result = await runExtensionSigningFlow(username, accountToken);
    output.textContent += '✅ Extension signing completed successfully.\n';
    output.textContent += `\n${JSON.stringify(result, null, 2)}\n`;
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
