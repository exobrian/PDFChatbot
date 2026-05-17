function showTab(type) {
    if (type === 'login') {
        document.getElementById('login-form').style.display = 'block';
        document.getElementById('signup-form').style.display = 'none';
        document.getElementById('btn-login').classList.add('active');
        document.getElementById('btn-signup').classList.remove('active');
    } else {
        document.getElementById('login-form').style.display = 'none';
        document.getElementById('signup-form').style.display = 'block';
        document.getElementById('btn-login').classList.remove('active');
        document.getElementById('btn-signup').classList.add('active');
    }
}

async function authAction(endpoint) {
    let payload = {};
    if (endpoint === 'login') {
        payload = {
            email: document.getElementById('l-email').value,
            password: document.getElementById('l-password').value
        };
    } else {
        payload = {
            username: document.getElementById('s-username').value,
            email: document.getElementById('s-email').value,
            password: document.getElementById('s-password').value
        };
    }

    const response = await fetch(`/${endpoint}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    
    const data = await response.json();
    if (response.ok) {
        if (endpoint === 'login') {
            window.location.href = '/';
        } else {
            alert("Registration successful! Proceed to login.");
            showTab('login');
        }
    } else {
        alert(data.error || "An authentication fault occurred.");
    }
}