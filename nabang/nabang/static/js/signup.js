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

document.addEventListener('DOMContentLoaded', function() {
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');
    const passwordMatch = document.getElementById('passwordMatch');
    const signupForm = document.getElementById('signup-form');

    function checkPasswordMatch() {
        if (password.value && confirmPassword.value) {
            if (password.value === confirmPassword.value) {
                passwordMatch.textContent = '비밀번호가 일치합니다.';
                passwordMatch.style.color = 'green';
            } else {
                passwordMatch.textContent = '비밀번호가 일치하지 않습니다.';
                passwordMatch.style.color = 'red';
            }
        } else {
            passwordMatch.textContent = '';
        }
    }

    password.addEventListener('input', checkPasswordMatch);
    confirmPassword.addEventListener('input', checkPasswordMatch);

    signupForm.addEventListener('submit', function(event) {
        if (password.value !== confirmPassword.value) {
            event.preventDefault();
            alert('비밀번호가 일치하지 않습니다.');
        }
    });
});