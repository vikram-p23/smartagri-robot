
    const toggle = document.getElementById('darkModeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const htmlEl = document.documentElement;

    // Load saved theme or system preference
    const savedTheme = localStorage.getItem('theme') ||
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

    // Apply theme on load
    if (savedTheme === 'dark') {
        htmlEl.classList.remove('light');
        htmlEl.setAttribute('data-bs-theme', 'dark');
        themeIcon.classList.remove('bi-moon');
        themeIcon.classList.add('bi-sun');
        toggle.checked = true;
    } else {
        htmlEl.classList.add('light');
        htmlEl.setAttribute('data-bs-theme', 'light');
        themeIcon.classList.remove('bi-sun');
        themeIcon.classList.add('bi-moon');
        toggle.checked = false;
    }

    // Toggle theme when clicked
    toggle.addEventListener('click', () => {
        if (htmlEl.classList.contains('light')) {
            htmlEl.classList.remove('light');
            htmlEl.setAttribute('data-bs-theme', 'dark');
            themeIcon.classList.remove('bi-moon');
            themeIcon.classList.add('bi-sun');
            localStorage.setItem('theme', 'dark');
        } else {
            htmlEl.classList.add('light');
            htmlEl.setAttribute('data-bs-theme', 'light');
            themeIcon.classList.remove('bi-sun');
            themeIcon.classList.add('bi-moon');
            localStorage.setItem('theme', 'light');
        }
    });

 document.getElementById('sensorBtn').addEventListener('click', () => {
                            window.location.href = "{{ url_for('sensordata') }}";
                        });


