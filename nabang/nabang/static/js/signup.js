document.addEventListener('DOMContentLoaded', function () {
    const signupForm = document.getElementById('signup-form');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');
    const passwordMatch = document.getElementById('passwordMatch');
    const privacyPolicyCheckbox = document.getElementById('agree');
    const submitButton = document.querySelector('.submit-button');

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

    function updateSubmitButtonState() {
        let allFilled = Array.from(signupForm.querySelectorAll('input:not([type=submit]), select'))
            .every(input => input.value.trim() !== '');
        let isPasswordMatching = password.value === confirmPassword.value;
        let isPrivacyPolicyChecked = privacyPolicyCheckbox.checked;

        submitButton.disabled = !(allFilled && isPasswordMatching && isPrivacyPolicyChecked);
        submitButton.style.opacity = submitButton.disabled ? '0.3' : '1';
        submitButton.style.cursor = submitButton.disabled ? 'default' : 'pointer';
    }

    password.addEventListener('input', function() {
        checkPasswordMatch();
        updateSubmitButtonState();
    });
    confirmPassword.addEventListener('input', function() {
        checkPasswordMatch();
        updateSubmitButtonState();
    });
    privacyPolicyCheckbox.addEventListener('change', updateSubmitButtonState);

    signupForm.addEventListener('submit', function(event) {
        if (password.value !== confirmPassword.value) {
            event.preventDefault();
            alert('비밀번호가 일치하지 않습니다.');
        } else if (!privacyPolicyCheckbox.checked) {
            event.preventDefault();
            alert('개인정보 처리방침에 동의해주시길 바랍니다.');
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    var checkbox = document.getElementById('privacy-policy');
    var submitButton = document.querySelector('.submit-button');

    // 페이지 로드 시 제출 버튼의 초기 상태 설정
    submitButton.disabled = !checkbox.checked;

    // 체크박스 상태 변경 시 제출 버튼 활성화/비활성화
    checkbox.addEventListener('change', function () {
        submitButton.disabled = !this.checked;
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const signupForm = document.getElementById('signup-form');
    const inputs = signupForm.querySelectorAll('input:not([type=submit]), select');
    const checkbox = document.getElementById('privacy-policy');
    const submitButton = document.querySelector('.submit-button');

    function updateButtonState() {
        let allFilled = Array.from(inputs).every(input => input.value.trim() !== '');
        let isCheckboxChecked = checkbox.checked;

        let canSubmit = allFilled && isCheckboxChecked;
        submitButton.disabled = !canSubmit;
        submitButton.style.opacity = canSubmit ? '1' : '0.3';
        submitButton.style.cursor = canSubmit ? 'pointer' : 'default';
    }

    inputs.forEach(input => input.addEventListener('input', updateButtonState));
    checkbox.addEventListener('change', updateButtonState);

    // 초기 버튼 상태 설정
    updateButtonState();
});

document.addEventListener('DOMContentLoaded', function () {
    const checkUsernameButton = document.getElementById('check-username-button');
    const usernameInput = document.getElementById('username');
    const usernameResult = document.getElementById('username-result');

    checkUsernameButton.addEventListener('click', function () {
        const username = usernameInput.value;

        fetch(`/check_username/?username=${username}`)
            .then(response => response.json())
            .then(data => {
                if (data.is_taken) {
                    usernameResult.textContent = '이미 사용 중인 아이디입니다.';
                    usernameResult.style.color = 'red';
                } else {
                    usernameResult.textContent = '사용 가능한 아이디입니다.';
                    usernameResult.style.color = 'green';
                }
            })
            .catch(error => console.error('Error:', error));
    });
});