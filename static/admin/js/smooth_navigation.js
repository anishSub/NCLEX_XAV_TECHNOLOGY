/* ========================================
   NCLEX Admin Panel - AGGRESSIVE Sidebar Scroll Fix
   Works with Django admin's full page reload
   ======================================== */

(function () {
  'use strict';

  // ===== ENSURE SCRIPT RUNS BEFORE ANYTHING ELSE =====

  // Save clicked link IMMEDIATELY on click
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initScrollFix);
  } else {
    initScrollFix();
  }

  function initScrollFix() {
    // Attach click handlers to ALL sidebar links
    attachClickHandlers();

    // Restore scroll position IMMEDIATELY
    restoreSidebarPosition();
  }

  function attachClickHandlers() {
    const allLinks = document.querySelectorAll('.sidebar a');

    allLinks.forEach(link => {
      link.addEventListener('click', function (e) {
        const sidebar = document.querySelector('.sidebar');

        // Save the exact element that was clicked
        const linkText = this.textContent.trim();
        const linkHref = this.getAttribute('href');

        sessionStorage.setItem('clickedLinkText', linkText);
        sessionStorage.setItem('clickedLinkHref', linkHref);

        // Save sidebar scroll position
        if (sidebar) {
          const scrollPos = sidebar.scrollTop;
          sessionStorage.setItem('sidebarScrollTop', scrollPos);
          console.log('Saved scroll position:', scrollPos);
        }
      });
    });
  }

  function restoreSidebarPosition() {
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) return;

    const savedLinkText = sessionStorage.getItem('clickedLinkText');
    const savedLinkHref = sessionStorage.getItem('clickedLinkHref');
    const savedScroll = sessionStorage.getItem('sidebarScrollTop');

    console.log('Restoring - Text:', savedLinkText, 'Href:', savedLinkHref, 'Scroll:', savedScroll);

    if (savedLinkHref) {
      // Method 1: Find the exact link by href
      const targetLink = sidebar.querySelector(`a[href="${savedLinkHref}"]`);

      if (targetLink) {
        console.log('Found target link:', targetLink);

        // Wait for layout to complete
        setTimeout(() => {
          const linkTop = targetLink.offsetTop;
          const sidebarHeight = sidebar.clientHeight;

          // Scroll so the link is near the top (not middle, for better UX)
          const scrollTarget = linkTop - 100; // 100px from top

          sidebar.scrollTop = Math.max(0, scrollTarget);
          console.log('Scrolled to:', sidebar.scrollTop);
        }, 100);

        return;
      }
    }

    // Method 2: Fallback to saved scroll position
    if (savedScroll) {
      setTimeout(() => {
        sidebar.scrollTop = parseInt(savedScroll);
        console.log('Used fallback scroll:', sidebar.scrollTop);
      }, 100);
    }
  }

  // ===== RUN MULTIPLE TIMES TO ENSURE IT WORKS =====
  // Django admin sometimes loads things in stages

  window.addEventListener('load', function () {
    console.log('Window loaded, restoring position...');
    setTimeout(restoreSidebarPosition, 200);
    setTimeout(restoreSidebarPosition, 500);
    setTimeout(restoreSidebarPosition, 1000);
  });

  // ===== FIX DOUBLE SELECTION BUG =====
  function fixDoubleSelection() {
    const parentItems = document.querySelectorAll('.nav-item.has-treeview');

    parentItems.forEach(parent => {
      const parentLink = parent.querySelector('.nav-link');
      const childLinks = parent.querySelectorAll('.nav-treeview .nav-link');

      let hasActiveChild = false;
      childLinks.forEach(child => {
        if (child.classList.contains('active')) {
          hasActiveChild = true;
        }
      });

      if (hasActiveChild && parentLink) {
        parentLink.classList.remove('active');
        parent.classList.add('menu-open');
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    setTimeout(fixDoubleSelection, 100);
    setTimeout(fixDoubleSelection, 500);
  });

  // ===== CLEAR ON LOGOUT =====
  document.addEventListener('DOMContentLoaded', function () {
    const logoutLinks = document.querySelectorAll('a[href*="logout"]');
    logoutLinks.forEach(link => {
      link.addEventListener('click', function () {
        sessionStorage.clear();
      });
    });
  });

})();

// ===== ALTERNATIVE: Use MutationObserver to detect when sidebar is ready =====
(function () {
  const observer = new MutationObserver(function (mutations) {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar && sidebar.children.length > 0) {
      const savedScroll = sessionStorage.getItem('sidebarScrollTop');
      if (savedScroll) {
        sidebar.scrollTop = parseInt(savedScroll);
        console.log('MutationObserver restored scroll:', savedScroll);
      }
    }
  });

  if (document.body) {
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    // Stop observing after 3 seconds
    setTimeout(() => observer.disconnect(), 3000);
  }
})();
