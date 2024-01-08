document.addEventListener('DOMContentLoaded', function() {
    var loginLink = document.querySelector('.nav-login-link');
    var closeButton = document.querySelector('.close-button');
    var popup = document.getElementById('login-popup');

    if (loginLink && closeButton && popup) {
        loginLink.addEventListener('click', function(event) {
            event.preventDefault();
            popup.style.display = 'flex'; // 팝업 표시
        });

        closeButton.addEventListener('click', function() {
            popup.style.display = 'none'; // 팝업 숨김
        });
    }
});