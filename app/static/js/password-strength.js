document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password1');
    const confirmPasswordInput = document.getElementById('password2');
    const strengthBar = document.querySelector('.progress-bar');
    const passwordFeedback = document.getElementById('passwordFeedback');
    const submitButton = document.getElementById('submitButton');
    const togglePassword1 = document.getElementById('togglePassword1');
    const togglePassword2 = document.getElementById('togglePassword2');
    
    // Password visibility toggles
    togglePassword1.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        this.querySelector('i').classList.toggle('bi-eye');
        this.querySelector('i').classList.toggle('bi-eye-slash');
    });
    
    togglePassword2.addEventListener('click', function() {
        const type = confirmPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        confirmPasswordInput.setAttribute('type', type);
        this.querySelector('i').classList.toggle('bi-eye');
        this.querySelector('i').classList.toggle('bi-eye-slash');
    });
    
    // Check password strength and update UI
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        const result = checkPasswordStrength(password);
        
        // Update progress bar
        strengthBar.style.width = result.strength + '%';
        
        // Update progress bar color
        if (result.strength < 40) {
            strengthBar.className = 'progress-bar bg-danger';
        } else if (result.strength < 70) {
            strengthBar.className = 'progress-bar bg-warning';
        } else {
            strengthBar.className = 'progress-bar bg-success';
        }
        
        // Update feedback text
        passwordFeedback.textContent = result.feedback;
        passwordFeedback.className = 'password-feedback ' + result.feedbackClass;
        
        // Update requirement list
        updateRequirementList(result);
        
        // Check if passwords match
        checkPasswordMatch();
        
        // Enable/disable submit button based on password validity
        submitButton.disabled = !(result.isValid && confirmPasswordInput.value === passwordInput.value);
    });
    
    // Check if passwords match
    confirmPasswordInput.addEventListener('input', checkPasswordMatch);
    
    function checkPasswordMatch() {
        if (confirmPasswordInput.value !== passwordInput.value) {
            confirmPasswordInput.classList.add('is-invalid');
            document.getElementById('confirmPasswordFeedback').textContent = 'Passwords do not match';
            submitButton.disabled = true;
        } else {
            confirmPasswordInput.classList.remove('is-invalid');
            document.getElementById('confirmPasswordFeedback').textContent = '';
            
            // Only enable if the password is also valid
            const result = checkPasswordStrength(passwordInput.value);
            submitButton.disabled = !result.isValid;
        }
    }
    
    function checkPasswordStrength(password) {
        let strength = 0;
        let feedback = '';
        let feedbackClass = '';
        let isValid = false;
        
        // Define requirements
        const hasMinLength = password.length >= 12;
        const hasUppercase = /[A-Z]/.test(password);
        const hasLowercase = /[a-z]/.test(password);
        const hasDigit = /[0-9]/.test(password);
        const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
        
        // Calculate strength
        if (hasMinLength) strength += 20;
        if (hasUppercase) strength += 20;
        if (hasDigit) strength += 20;
        if (hasLowercase) strength += 20;
        if (hasSpecialChar) strength += 20;
        
        // Determine feedback
        if (password.length === 0) {
            feedback = 'Enter a password';
            feedbackClass = 'text-muted';
        } else if (password.length < 6) {
            feedback = 'Too short';
            feedbackClass = 'text-danger';
        } else if (strength < 50) {
            feedback = 'Weak password';
            feedbackClass = 'text-danger';
        } else if (strength < 75) {
            feedback = 'Medium strength password';
            feedbackClass = 'text-warning';
        } else if (strength < 100) {
            feedback = 'Strong password';
            feedbackClass = 'text-success';
        } else {
            feedback = 'Very strong password';
            feedbackClass = 'text-success';
        }
        
        // Check if all requirements are met
        isValid = hasMinLength && hasUppercase && hasLowercase && hasSpecialChar;
        
        return {
            strength,
            feedback,
            feedbackClass,
            isValid,
            hasMinLength,
            hasDigit,
            hasUppercase,
            hasLowercase,
            hasSpecialChar
        };
    }
    
    function updateRequirementList(result) {
        // Update requirement list icons and colors
        document.getElementById('reqLength').className = result.hasMinLength ? 'valid-requirement' : 'invalid-requirement';
        document.getElementById('reqLength').innerHTML = result.hasMinLength ? 
            '<i class="bi bi-check-circle-fill"></i> At least 12 characters long' : 
            '<i class="bi bi-x-circle-fill"></i> At least 12 characters long';

        document.getElementById('reqDigit').className = result.hasDigit ? 'valid-requirement' : 'invalid-requirement';
        document.getElementById('reqDigit').innerHTML = result.hasDigit ? 
            '<i class="bi bi-check-circle-fill"></i> 1 number [0-9]' : 
            '<i class="bi bi-x-circle-fill"></i> 1 number [0-9]';
        
        document.getElementById('reqUppercase').className = result.hasUppercase ? 'valid-requirement' : 'invalid-requirement';
        document.getElementById('reqUppercase').innerHTML = result.hasUppercase ? 
            '<i class="bi bi-check-circle-fill"></i> 1 uppercase letter' : 
            '<i class="bi bi-x-circle-fill"></i> 1 uppercase letter';
        
        document.getElementById('reqLowercase').className = result.hasLowercase ? 'valid-requirement' : 'invalid-requirement';
        document.getElementById('reqLowercase').innerHTML = result.hasLowercase ? 
            '<i class="bi bi-check-circle-fill"></i> 1 lowercase letter' : 
            '<i class="bi bi-x-circle-fill"></i> 1 lowercase letter';
        
        document.getElementById('reqSpecial').className = result.hasSpecialChar ? 'valid-requirement' : 'invalid-requirement';
        document.getElementById('reqSpecial').innerHTML = result.hasSpecialChar ? 
            '<i class="bi bi-check-circle-fill"></i> 1 special character' : 
            '<i class="bi bi-x-circle-fill"></i> 1 special character';
    }
    
    // Form submission handler
    document.getElementById('userForm').addEventListener('submit', function(e) {
        const password = passwordInput.value;
        const result = checkPasswordStrength(password);
        
        if (!result.isValid) {
            e.preventDefault();
            alert('Please ensure your password meets all requirements.');
            return;
        }
        
        if (password !== confirmPasswordInput.value) {
            e.preventDefault();
            alert('Passwords do not match.');
            return;
        }
        
        // If we get here, the form is valid and can be submitted
    });
});
