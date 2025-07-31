import { registerPasskey } from './register.js';
import { loginWithPasskey } from './auth.js';

export async function handleFormSubmit(event) {
  event.preventDefault();

  const form = event.target;
  const action = form.dataset.action;
  const username = form.username?.value.trim();
  const account = form.account?.value.trim();
  const output = document.querySelector('#output');

  if (!username && action==='register') {
    output.textContent = '⚠️ Please enter required fields.';
    return;
  }

  console.log('username', username)
  try {
    if (action === 'register') {
      const result = await registerPasskey(username, account);
      output.textContent = '✅ Registered successfully';
      console.log(JSON.stringify(result, null, 2));
    } else if (action === 'login') {
      const result = await loginWithPasskey(username);
      output.textContent = '✅ Authentication successful';
      console.log(JSON.stringify(result, null, 2));
    }else if(action === 'loginwithpasskey'){
       const result = await loginWithPasskey();
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
