import { registerPasskey } from './register.js';

document.querySelector("#register-btn").addEventListener("click", async () => {
  const username = document.querySelector("#username").value;
  const output = document.querySelector("#output");

  try {
    const result = await registerPasskey(username);
    output.textContent = JSON.stringify(result, null, 2);
  } catch (err) {
    output.textContent = "❌ " + err.message;
  }
});
