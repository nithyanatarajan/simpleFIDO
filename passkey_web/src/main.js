import {registerPasskey} from './register.js';
import {loginWithPasskey} from './auth.js';
import {getAccountToken} from './token.js';

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
    const token = await getAccountToken(username, password, accountId);
    sessionStorage.setItem('accountToken', token);
    sessionStorage.setItem('username', username);
    output.textContent = '✅ Token generated and stored in session.';
  } catch (err) {
    console.error(err);
    output.textContent = `❌ Error: ${err?.response?.data?.detail || err.message || 'Unknown error'}`;
  }
}

export async function handleRegister(event) {
  event.preventDefault();
  const form = event.target;
  const username = form.username?.value.trim() || sessionStorage.getItem('username');
  const accountToken = sessionStorage.getItem('accountToken');
  const output = document.querySelector('#output');

  if (!username || !accountToken) {
    output.textContent = '⚠️ Username and accountToken required. Please generate token first.';
    return;
  }

  try {
    const result = await registerPasskey(username, accountToken);
    output.textContent = '✅ Registered successfully.';
    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error(err);
    output.textContent = `❌ Error: ${err?.response?.data?.detail || err.message || 'Unknown error'}`;
  }
}

export async function handleLogin(event) {
  event.preventDefault();
  const form = event.target;
  const username = form.username?.value.trim() || sessionStorage.getItem('username');
  const accountToken = sessionStorage.getItem('accountToken');
  const output = document.querySelector('#output');

  if (!username || !accountToken) {
    output.textContent = '⚠️ Username and accountToken required. Please generate token first.';
    return;
  }

  try {
    const result = await loginWithPasskey(username, accountToken);
    output.textContent = '✅ Authentication successful.';
    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error(err);
    output.textContent = `❌ Error: ${err?.response?.data?.detail || err.message || 'Unknown error'}`;
  }
}

const handlers = {
  generate: handleGenerateToken,
  register: handleRegister,
  login: handleLogin
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
