document.addEventListener("DOMContentLoaded", () => {
    const password = document.getElementById("password");
    const strengthBar = document.getElementById("strength-bar");
    const toggleShow = document.getElementById("toggle-show");
    const generateBtn = document.getElementById("generate-btn");

    function updateStrength(value) {
        let strength = 0;
        if (value.length >= 6) strength++;
        if (value.length >= 10) strength++;
        if (/[A-Z]/.test(value)) strength++;
        if (/[0-9]/.test(value)) strength++;
        if (/[^A-Za-z0-9]/.test(value)) strength++;

        const percent = (strength / 5) * 100;
        strengthBar.style.width = percent + "%";
        strengthBar.style.background =
            percent < 40 ? "red" :
            percent < 60 ? "orange" :
            percent < 80 ? "yellow" :
            "green";
    }

    password.addEventListener("input", (e) => {
        updateStrength(e.target.value);
    });

    toggleShow.addEventListener("click", () => {
        if (password.type === "password") {
            password.type = "text";
            toggleShow.textContent = "Hide";
        } else {
            password.type = "password";
            toggleShow.textContent = "Show";
        }
    });

    generateBtn.addEventListener("click", () => {
        const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:,.<>?";
        let generated = "";
        for (let i = 0; i < 16; i++) {
            generated += charset.charAt(Math.floor(Math.random() * charset.length));
        }
        password.value = generated;
        updateStrength(generated);
    });
});