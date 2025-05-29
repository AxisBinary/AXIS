document.getElementById('accessCodeForm').addEventListener('submit', (event) => {
  event.preventDefault(); // Prevent default form submission
  event.stopImmediatePropagation(); // Stop login.js submit handler to prevent alert

  const accessCode = document.getElementById('accessCode').value.trim();
  const accessPassword = document.getElementById('accessPassword').value.trim();
  const validationMessageCode = document.getElementById('validationMessageCode');
  const validationMessagePassword = document.getElementById('validationMessagePassword');

  // Clear previous validation messages
  validationMessageCode.textContent = '';
  validationMessagePassword.textContent = '';

  // Check for empty fields (reinforcing login.js validation)
  if (!accessCode) {
    validationMessageCode.textContent = 'Access code is required.';
    document.getElementById('accessCode').focus();
    return;
  }
  if (!accessPassword) {
    validationMessagePassword.textContent = 'Password is required.';
    document.getElementById('accessPassword').focus();
    return;
  }

  // Send to backend (login.js already validated format)
  window.electronAPI.sendLogin(accessCode, accessPassword);

  // Handle backend response
  window.electronAPI.onLoginResponse((response) => {
    if (response.success) {
      // Redirect immediately without success message
      window.electronAPI.loadDashboard();
    } else {
      validationMessagePassword.textContent = response.message;
    }
  });
});