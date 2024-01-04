function showLoginPopup() {
    var popup = document.getElementById('login-popup');
    popup.style.display = 'flex'; // 팝업을 flex로 설정하여 보여줌
}

// 로그인 팝업 숨기기 함수
function hideLoginPopup() {
    document.getElementById('login-popup').style.display = 'none';
}

// 로그인 링크 이벤트 리스너
document.querySelector('.nav-login-link').addEventListener('click', function(event) {
    event.preventDefault();
    showLoginPopup();
});

// 팝업 닫기 버튼 이벤트 리스너
document.querySelector('.close-button').addEventListener('click', function() {
    hideLoginPopup(); // 로그인 팝업 숨김
});

document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.getElementById('signup-form');

    signupForm.addEventListener('submit', function(event) {
        const password = document.getElementById('password').value;
        const confirm_password = document.getElementById('confirm_password').value;
        const agree = document.getElementById('agree').checked;

        // 비밀번호 일치 여부 검증
        if (password !== confirm_password) {
            event.preventDefault(); // 폼 제출 중단
            alert('비밀번호가 일치하지 않습니다.');
        }

        // 개인정보 처리방침 동의 여부 검증
        if (!agree) {
            event.preventDefault(); // 폼 제출 중단
            alert('개인정보 처리방침에 동의해주시길 바랍니다.');
        }
    });
});