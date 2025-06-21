document.addEventListener("DOMContentLoaded", () => {
  const loginBtn = document.getElementById("loginBtn");

  loginBtn.addEventListener("click", async () => {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const errorText = document.getElementById("error");

    if (!username || !password) {
      errorText.textContent = "Username and password are required.";
      errorText.classList.remove("hidden");
      return;
    }

    try {
      const res = await fetch("http://localhost:8010/auth/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
        username,
        password,
        grant_type: "password"
        })
      });

      if (res.ok) {
        const data = await res.json();
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("username", username);
        errorText.classList.add("hidden");
        window.location.href = "chat.html";
      } else {
        errorText.textContent = "Login failed. Please check your credentials.";
        errorText.classList.remove("hidden");
      }
    } catch (err) {
      console.error("Login error:", err);
      errorText.textContent = "Server error. Try again later.";
      errorText.classList.remove("hidden");
    }
  });
});
