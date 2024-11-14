window.fbAsyncInit = function() {
    FB.init({
        appId      : 'YOUR_APP_ID', // Replace with your Facebook App ID
        cookie     : true,
        xfbml      : true,
        version    : 'v12.0'
    });
      
    FB.AppEvents.logPageView();   
      
    FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
    });
};

function statusChangeCallback(response) {
    if (response.status === 'connected') {
        console.log('Logged in and authenticated');
        setElements(true);
        testAPI();
    } else {
        console.log('Not authenticated');
        setElements(false);
    }
}

function checkLoginState() {
    FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
    });
}

function testAPI() {
    FB.api('/me?fields=name,email', function(response) {
        if (response && !response.error) {
            console.log(response);
            buildProfile(response);
        }
    });
}

function buildProfile(user) {
    let profile = `
        <h3>Welcome ${user.name}!</h3>
        <ul class="list-group">
            <li class="list-group-item">User ID: ${user.id}</li>
            <li class="list-group-item">Email: ${user.email}</li>
        </ul>
    `;
    document.getElementById('status').innerHTML = profile;
}

function setElements(isLoggedIn) {
    if (isLoggedIn) {
        document.getElementById('status').style.display = 'block';
        document.querySelector('.fb-login-button').style.display = 'none';
    } else {
        document.getElementById('status').style.display = 'none';
        document.querySelector('.fb-login-button').style.display = 'block';
    }
}
