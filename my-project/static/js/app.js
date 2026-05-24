/**
 * Phase 7 — UI/UX polish: toast, GSAP, skeleton, HTMX hooks, before/after slider.
 */
(function () {
    'use strict';

    const TOAST_DURATION = 4500;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // --- Toast notification ---
    function getToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.setAttribute('aria-live', 'polite');
            container.setAttribute('aria-atomic', 'true');
            document.body.appendChild(container);
        }
        return container;
    }

    function toastIcon(type) {
        if (type === 'success') return '<i data-lucide="check-circle" class="icon-inline icon-md"></i>';
        if (type === 'error') return '<i data-lucide="x-circle" class="icon-inline icon-md"></i>';
        return '<i data-lucide="info" class="icon-inline icon-md"></i>';
    }

    // Khoi tao / cap nhat icon Lucide sau render DOM hoac HTMX swap.
    window.refreshLucideIcons = function (root) {
        if (typeof lucide === 'undefined' || !lucide.createIcons) return;
        var options = { attrs: { 'aria-hidden': 'true' } };
        if (root) {
            options.root = root;
        }
        lucide.createIcons(options);
    };

    window.showToast = function (message, type) {
        type = type || 'info';
        if (!message) return;

        const container = getToastContainer();
        const item = document.createElement('div');
        item.className = 'toast-item toast-' + type;
        item.setAttribute('role', 'alert');

        item.innerHTML =
            '<span class="toast-icon">' + toastIcon(type) + '</span>' +
            '<span class="toast-message">' + escapeHtml(message) + '</span>' +
            '<button type="button" class="toast-close" aria-label="Đóng thông báo">×</button>';

        const closeBtn = item.querySelector('.toast-close');
        closeBtn.addEventListener('click', function () {
            removeToast(item);
        });

        container.appendChild(item);
        refreshLucideIcons(item);

        if (!prefersReducedMotion && typeof gsap !== 'undefined') {
            gsap.from(item, { opacity: 0, x: 24, duration: 0.3, ease: 'power2.out' });
        }

        setTimeout(function () {
            removeToast(item);
        }, TOAST_DURATION);
    };

    function removeToast(item) {
        if (!item || !item.parentNode) return;
        if (!prefersReducedMotion && typeof gsap !== 'undefined') {
            gsap.to(item, {
                opacity: 0,
                x: 24,
                duration: 0.2,
                onComplete: function () {
                    item.remove();
                },
            });
        } else {
            item.remove();
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Chuyen Django messages sang toast va an alert cu.
    function migrateDjangoMessages() {
        document.querySelectorAll('[data-django-message]').forEach(function (el) {
            const message = el.getAttribute('data-django-message');
            const type = el.getAttribute('data-django-type') || 'info';
            showToast(message, type);
            el.remove();
        });
    }

    // --- HTMX progress bar ---
    function ensureProgressBar() {
        let bar = document.getElementById('htmx-progress-bar');
        if (!bar) {
            bar = document.createElement('div');
            bar.id = 'htmx-progress-bar';
            bar.className = 'htmx-progress-bar';
            bar.setAttribute('aria-hidden', 'true');
            document.body.appendChild(bar);
        }
        return bar;
    }

    function startProgress() {
        const bar = ensureProgressBar();
        bar.classList.remove('is-done');
        bar.classList.add('is-active');
    }

    function finishProgress() {
        const bar = ensureProgressBar();
        bar.classList.remove('is-active');
        bar.classList.add('is-done');
        setTimeout(function () {
            bar.classList.remove('is-done');
        }, 400);
    }

    // --- Processing skeleton ---
    function getProcessingSkeletonHtml() {
        const tpl = document.getElementById('processing-skeleton-template');
        if (tpl) return tpl.innerHTML;
        return (
            '<div class="processing-skeleton card bg-white border border-[#E5E7EB] shadow-sm rounded-xl">' +
            '<div class="card-body space-y-4">' +
            '<div class="skeleton-block h-6 w-48"></div>' +
            '<div class="grid grid-cols-1 md:grid-cols-2 gap-4">' +
            '<div class="skeleton-block aspect-video"></div>' +
            '<div class="skeleton-block aspect-video"></div>' +
            '</div>' +
            '<div class="skeleton-block h-10 w-full"></div>' +
            '</div></div>'
        );
    }

    function showProcessingSkeleton(targetId) {
        const target = document.getElementById(targetId);
        if (target) {
            target.innerHTML = getProcessingSkeletonHtml();
        }
    }

    // --- GSAP page animations ---
    function animatePageEntrance() {
        if (prefersReducedMotion || typeof gsap === 'undefined') {
            document.querySelectorAll('.animate-stagger-item').forEach(function (el) {
                el.style.opacity = '1';
                el.style.transform = 'none';
            });
            return;
        }

        const pageContent = document.getElementById('page-content');
        if (pageContent) {
            gsap.from(pageContent, { opacity: 0, y: 12, duration: 0.25, ease: 'power2.out' });
        }

        const staggerItems = document.querySelectorAll('.animate-stagger-item');
        if (staggerItems.length) {
            gsap.to(staggerItems, {
                opacity: 1,
                y: 0,
                duration: 0.35,
                stagger: 0.07,
                ease: 'power2.out',
                delay: 0.05,
            });
        }
    }

    function animateSwapTarget(target) {
        if (prefersReducedMotion || typeof gsap === 'undefined' || !target) return;
        gsap.from(target, { opacity: 0, y: 12, duration: 0.25, ease: 'power2.out' });
    }

    // --- HTMX toast tu partial ket qua / loi ---
    function detectHtmxToast(target) {
        if (!target) return;
        const successEl = target.querySelector('[data-toast-success]');
        const errorEl = target.querySelector('[data-toast-error]');
        if (successEl) {
            showToast(successEl.getAttribute('data-toast-success'), 'success');
        }
        if (errorEl) {
            showToast(errorEl.getAttribute('data-toast-error'), 'error');
        }
    }

    // --- Before / After slider (Alpine.js component) ---
    window.beforeAfterSlider = function () {
        return {
            position: 50,
            dragging: false,

            updateFromEvent: function (event) {
                const rect = this.$refs.container.getBoundingClientRect();
                let clientX = event.clientX;
                if (event.touches && event.touches.length) {
                    clientX = event.touches[0].clientX;
                }
                const x = clientX - rect.left;
                const pct = Math.max(0, Math.min(100, (x / rect.width) * 100));
                this.position = Math.round(pct);
            },

            startDrag: function (event) {
                this.dragging = true;
                this.$refs.container.classList.add('is-dragging');
                this.updateFromEvent(event);
            },

            onDrag: function (event) {
                if (!this.dragging) return;
                this.updateFromEvent(event);
            },

            endDrag: function () {
                this.dragging = false;
                this.$refs.container.classList.remove('is-dragging');
            },

            onKeydown: function (event) {
                if (event.key === 'ArrowLeft') {
                    this.position = Math.max(0, this.position - 2);
                    event.preventDefault();
                } else if (event.key === 'ArrowRight') {
                    this.position = Math.min(100, this.position + 2);
                    event.preventDefault();
                }
            },
        };
    };

    function revealProcessingResult(container) {
        // Ep hien thi ket qua HTMX — tranh bi an boi animate-stagger-item / GSAP.
        if (!container) return;

        container.style.opacity = '1';
        container.style.transform = 'none';
        container.style.visibility = 'visible';

        container.querySelectorAll('.processing-result-card, .card, .animate-stagger-item').forEach(function (el) {
            el.style.opacity = '1';
            el.style.transform = 'none';
            el.style.visibility = 'visible';
        });
    }

    function animateStaggerIn(container) {
        // Hoat animation cho noi dung HTMX moi inject (partial ket qua xu ly).
        if (!container) return;

        // Ket qua xu ly anh — chi can hien ngay, khong dung stagger.
        if (container.id === 'process-result' || container.id === 'pipeline-result') {
            revealProcessingResult(container);
            return;
        }

        const items = container.querySelectorAll('.animate-stagger-item');
        if (!items.length) {
            animateSwapTarget(container);
            return;
        }

        if (prefersReducedMotion || typeof gsap === 'undefined') {
            items.forEach(function (el) {
                el.style.opacity = '1';
                el.style.transform = 'none';
            });
            return;
        }

        gsap.to(items, {
            opacity: 1,
            y: 0,
            duration: 0.35,
            stagger: 0.07,
            ease: 'power2.out',
        });
    }

    // Lay CSRF token tu meta tag hoac cookie de HTMX POST hoat dong voi Django.
    function getCsrfToken() {
        var meta = document.querySelector('meta[name="csrf-token"]');
        if (meta && meta.content) {
            return meta.content;
        }
        var match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : '';
    }

    document.body.addEventListener('htmx:configRequest', function (event) {
        var token = getCsrfToken();
        if (token) {
            event.detail.headers['X-CSRFToken'] = token;
        }
    });

    // --- Khoi tao su kien ---
    document.addEventListener('DOMContentLoaded', function () {
        migrateDjangoMessages();
        animatePageEntrance();
        refreshLucideIcons();
    });

    document.body.addEventListener('htmx:beforeRequest', function (event) {
        startProgress();
        const target = event.detail.target;
        if (target && (target.id === 'process-result' || target.id === 'pipeline-result')) {
            showProcessingSkeleton(target.id);
        }
    });

    document.body.addEventListener('htmx:afterRequest', function (event) {
        finishProgress();

        // Thong bao khi xoa anh admin thanh cong.
        var trigger = event.detail.xhr && event.detail.xhr.getResponseHeader('HX-Trigger');
        if (trigger && trigger.indexOf('adminImageDeleted') !== -1 && event.detail.successful) {
            showToast('Đã xóa ảnh khỏi hệ thống.', 'success');
        }
        if (trigger && trigger.indexOf('adminUserDeleted') !== -1 && event.detail.successful) {
            showToast('Đã xóa tài khoản người dùng.', 'success');
        }
    });

    document.body.addEventListener('htmx:afterSwap', function (event) {
        const target = event.detail.target;
        revealProcessingResult(
            target.id === 'process-result' || target.id === 'pipeline-result' ? target : null
        );
        animateStaggerIn(target);
        detectHtmxToast(target);
        refreshLucideIcons(target);

        if (target.id === 'history-table' ||
            target.id === 'admin-users-table' ||
            target.id === 'admin-images-table' ||
            target.id === 'admin-algorithms-table' ||
            target.id === 'admin-jobs-table' ||
            target.id === 'admin-logs-table') {
            animateSwapTarget(target);
        }
    });

    // Dam bao hien thi sau khi HTMX settle (phong truong hop afterSwap som).
    document.body.addEventListener('htmx:afterSettle', function (event) {
        const target = event.detail.target;
        if (target && (target.id === 'process-result' || target.id === 'pipeline-result')) {
            revealProcessingResult(target);
        }
    });

    document.body.addEventListener('htmx:responseError', function (event) {
        showToast('Yêu cầu thất bại. Vui lòng thử lại.', 'error');
    });
})();
