import { registerPasskey } from './register.js';
import { loginWithPasskey } from './auth.js';

export async function handleFormSubmit(event) {
  event.preventDefault();

  const form = event.target;
  const action = form.dataset.action;
  const username = form.username?.value.trim();
  const accountToken = form.accountToken?.value.trim(); // Optional for register
  const output = document.querySelector('#output');

  if (!username || (action === 'login' && !accountToken)) {
    output.textContent = '⚠️ Please enter required fields.';
    return;
  }

  try {
    if (action === 'register') {
      const result = await registerPasskey(username);
      output.textContent = '✅ Registered successfully';
      console.log(JSON.stringify(result, null, 2));
    } else if (action === 'login') {
      const result = await loginWithPasskey(username, accountToken);
      output.textContent = '✅ Authentication successful';
      console.log(JSON.stringify(result, null, 2));
    }
  } catch (err) {
    console.error(err);
    const errorMessage = err?.response?.data?.detail || err.message || 'Unknown error';
    output.textContent = `❌ ${action === 'register' ? 'Registration' : 'Authentication'} failed: ${errorMessage}`;
  }
}

// Attach submit listeners to all forms on load
document.querySelectorAll('form[data-action]').forEach(form => {
  form.addEventListener('submit', handleFormSubmit);
});
