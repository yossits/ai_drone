// Theme Selector
document.addEventListener("DOMContentLoaded", function () {
  const themeToggle = document.getElementById("theme-toggle");
  const themeDropdown = document.getElementById("theme-dropdown");
  const themeOptions = document.querySelectorAll(".theme-option");
  const body = document.body;

  // פונקציה לעדכון ערכת הנושא
  function setTheme(theme) {
    // הסרת כל ערכות הנושא
    body.classList.remove("theme-light", "theme-medium", "theme-dark");
    
    // הוספת ערכת הנושא הנבחרת
    body.classList.add(`theme-${theme}`);
    
    // עדכון localStorage
    localStorage.setItem("theme", theme);
    
    // עדכון אייקון בכפתור
    const icons = {
      light: "☀️",
      medium: "🌓",
      dark: "🌙"
    };
    themeToggle.querySelector("span").textContent = icons[theme];
    
    // עדכון סימון בחלונית
    themeOptions.forEach(option => {
      option.classList.remove("active");
      if (option.dataset.theme === theme) {
        option.classList.add("active");
      }
    });
    
    // סגירת החלונית
    themeDropdown.classList.remove("show");
  }

  // טעינת ערכת נושא שמורה
  const savedTheme = localStorage.getItem("theme") || "light";
  setTheme(savedTheme);

  // פתיחה/סגירה של חלונית בחירה
  themeToggle.addEventListener("click", function (e) {
    e.stopPropagation();
    themeDropdown.classList.toggle("show");
  });

  // בחירת ערכת נושא מהרשימה
  themeOptions.forEach(option => {
    option.addEventListener("click", function () {
      const selectedTheme = this.dataset.theme;
      setTheme(selectedTheme);
    });
  });

  // סגירת החלונית בלחיצה מחוץ לה
  document.addEventListener("click", function (e) {
    if (!themeToggle.contains(e.target) && !themeDropdown.contains(e.target)) {
      themeDropdown.classList.remove("show");
    }
  });

  // Sidebar Toggle
  const sidebarToggle = document.getElementById("sidebar-toggle");
  const sidebar = document.getElementById("sidebar");

  // בדיקה שהאלמנטים קיימים
  if (!sidebarToggle) {
    console.error("sidebar-toggle button not found");
  }
  if (!sidebar) {
    console.error("sidebar element not found");
  }

  if (sidebarToggle && sidebar) {
    console.log("Sidebar toggle initialized successfully");
    
    // פונקציה לכיווץ/הרחבת התפריט
    function toggleSidebar(e) {
      e.preventDefault();
      e.stopPropagation();
      
      console.log("Toggle button clicked");
      
      // בדיקה אם זה מובייל
      const isMobile = window.innerWidth <= 768;
      
      if (isMobile) {
        // במובייל - פתיחה/סגירה עם class "open"
        sidebar.classList.toggle("open");
    } else {
        // בדסקטופ - כיווץ/הרחבה
        sidebar.classList.toggle("collapsed");
        document.body.classList.toggle("sidebar-collapsed");
        
        // עדכון header
        const header = document.querySelector(".header");
        if (header) {
          const isCollapsed = sidebar.classList.contains("collapsed");
          if (isCollapsed) {
            header.classList.add("collapsed");
          } else {
            header.classList.remove("collapsed");
          }
        }
        
        // שמירת מצב ב-localStorage
        const isCollapsed = sidebar.classList.contains("collapsed");
        localStorage.setItem("sidebarCollapsed", isCollapsed);
    }
      
      console.log("Sidebar toggled, mobile:", isMobile);
    }

    // טעינת מצב שמור (רק בדסקטופ)
    const savedState = localStorage.getItem("sidebarCollapsed");
    if (savedState === "true" && window.innerWidth > 768) {
      sidebar.classList.add("collapsed");
      document.body.classList.add("sidebar-collapsed");
      const header = document.querySelector(".header");
      if (header) {
        header.classList.add("collapsed");
      }
      console.log("Loaded saved collapsed state");
    }

    // הוספת event listener לכפתור
    sidebarToggle.addEventListener("click", toggleSidebar);
    console.log("Event listener added to sidebar toggle");
    
    // במובייל - סגירת sidebar בלחיצה מחוץ לו
  if (window.innerWidth <= 768) {
      document.addEventListener("click", function(e) {
        if (sidebar && !sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
          sidebar.classList.remove("open");
        }
      });
    }
  } else {
    console.error("Failed to initialize sidebar toggle - missing elements");
  }

  // Mobile Menu Toggle
  const mobileMenuToggle = document.getElementById("mobile-menu-toggle");
  if (mobileMenuToggle && sidebar) {
    mobileMenuToggle.addEventListener("click", function(e) {
      e.preventDefault();
      e.stopPropagation();
      sidebar.classList.toggle("open");
    });
  }
});
