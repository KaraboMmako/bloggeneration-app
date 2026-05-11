document.addEventListener('DOMContentLoaded', () => {

    // ── Profile avatar dropdown ───────────────────────────────────────────────
    const avatarBtn  = document.getElementById('profile-avatar-btn');
    const profileDrop = document.getElementById('profile-dropdown');
    if (avatarBtn && profileDrop) {
        avatarBtn.addEventListener('click', e => {
            e.stopPropagation();
            const isOpen = profileDrop.classList.toggle('open');
            avatarBtn.setAttribute('aria-expanded', isOpen);
        });

        document.addEventListener('click', e => {
            if (!profileDrop.contains(e.target) && e.target !== avatarBtn) {
                profileDrop.classList.remove('open');
                avatarBtn.setAttribute('aria-expanded', 'false');
            }
        });

        document.addEventListener('keydown', e => {
            if (e.key === 'Escape') {
                profileDrop.classList.remove('open');
                avatarBtn.setAttribute('aria-expanded', 'false');
            }
        });
    }

    // ── Date filter toggle ────────────────────────────────────────────────────
    const dateToggle = document.getElementById('date-filter-toggle');
    const datePanel  = document.getElementById('date-filter-panel');
    if (dateToggle && datePanel) {
        dateToggle.addEventListener('click', () => {
            const isOpen = datePanel.classList.toggle('expanded');
            dateToggle.classList.toggle('active', isOpen);
        });
    }

    // ── Form submit spinners ──────────────────────────────────────────────────
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', () => {
            const btn = form.querySelector('button[type="submit"]');
            if (!btn) return;
            if (form.classList.contains('delete-blog-form')) return;
            btn.disabled = true;
            btn.dataset.originalText = btn.innerHTML;
            btn.innerHTML = '<span class="btn-spinner"></span>';
        });
    });

    // ── Regenerate blog confirmation ──────────────────────────────────────────
    document.querySelectorAll('.regen-blog-form').forEach(form => {
        form.addEventListener('submit', e => {
            const tile = form.closest('.blog-tile');
            const name = tile ? tile.querySelector('h3')?.textContent?.trim() : 'this blog';
            if (!confirm(`Regenerate "${name}"? All existing sections and images will be replaced.`)) {
                e.preventDefault();
            }
        });
    });

    // ── Delete blog confirmation ──────────────────────────────────────────────
    document.querySelectorAll('.delete-blog-form').forEach(form => {
        form.addEventListener('submit', e => {
            const tile  = form.closest('.blog-tile');
            const name  = tile ? tile.querySelector('h3')?.textContent?.trim() : 'this blog';
            if (!confirm(`Delete "${name}"? This cannot be undone.`)) {
                e.preventDefault();
            }
        });
    });

    // ── Copy Blog to clipboard ────────────────────────────────────────────────
    const copyBtn = document.getElementById('copy-blog-btn');
    if (!copyBtn) return;

    copyBtn.addEventListener('click', async () => {
        const title = copyBtn.dataset.blogTitle || 'Blog';
        const cards  = document.querySelectorAll('#blog-sections .section-card');

        // Build HTML and plain-text representations
        let html  = `<h1>${title}</h1>\n\n`;
        let plain = `${title}\n${'='.repeat(title.length)}\n\n`;

        // Hero image (if any)
        const heroImg = document.querySelector('.hero-image-card img');
        if (heroImg) {
            html  += `<img src="${heroImg.src}" alt="${heroImg.alt}" style="max-width:100%;margin-bottom:24px;">\n\n`;
            plain += `[Hero image: ${heroImg.src}]\n\n`;
        }

        cards.forEach(card => {
            const heading  = card.dataset.sectionHeading || '';
            const content  = card.querySelector('.section-content');
            const sectionImg = card.querySelector('.section-image img');

            if (heading) {
                html  += `<h2>${heading}</h2>\n`;
                plain += `\n${heading}\n${'-'.repeat(heading.length)}\n`;
            }

            if (sectionImg) {
                html  += `<img src="${sectionImg.src}" alt="${sectionImg.alt}" style="max-width:100%;margin:16px 0;">\n`;
                plain += `[Image: ${sectionImg.src}]\n`;
            }

            if (content) {
                html  += `${content.innerHTML}\n\n`;
                plain += `${(content.innerText || '').trim()}\n\n`;
            }
        });

        try {
            await navigator.clipboard.write([
                new ClipboardItem({
                    'text/html':  new Blob([html],  { type: 'text/html' }),
                    'text/plain': new Blob([plain], { type: 'text/plain' }),
                }),
            ]);
        } catch {
            // Fallback: plain text only
            await navigator.clipboard.writeText(plain).catch(() => {});
        }

        // Visual feedback
        const originalHTML = copyBtn.innerHTML;
        copyBtn.classList.add('copy-blog-btn--copied');
        copyBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Copied!`;

        setTimeout(() => {
            copyBtn.innerHTML = originalHTML;
            copyBtn.classList.remove('copy-blog-btn--copied');
        }, 2500);
    });
});
