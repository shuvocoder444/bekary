/**
 * BakeMaster Global Translation Engine
 * Handles instantaneous client-side translation across SPA swaps and HTMX navigation.
 */

(function () {
    window.BakeMasterI18n = {
        lang: localStorage.getItem('django_language') || (document.documentElement.lang === 'bn' ? 'bn' : 'en'),
        dict: {},

        setDict(data) {
            this.dict = data || {};
        },

        setLang(targetLang) {
            this.lang = targetLang;
            localStorage.setItem('django_language', targetLang);
            document.cookie = `django_language=${targetLang}; path=/; max-age=31536000; SameSite=Lax`;
            document.documentElement.lang = targetLang;
            this.translatePage();
        },

        t(text) {
            if (!text || this.lang !== 'bn') return text;
            const clean = text.trim();
            return this.dict[clean] || text;
        },

        // Fast DOM tree text node walker
        translatePage(root) {
            if (this.lang !== 'bn') return;
            const container = root || document.body;
            if (!container) return;

            const walker = document.createTreeWalker(
                container,
                NodeFilter.SHOW_TEXT,
                {
                    acceptNode(node) {
                        // Skip scripts, styles, inputs, textareas
                        const parent = node.parentElement;
                        if (!parent) return NodeFilter.FILTER_REJECT;
                        const tag = parent.tagName;
                        if (['SCRIPT', 'STYLE', 'CODE', 'PRE', 'NOSCRIPT'].includes(tag)) {
                            return NodeFilter.FILTER_REJECT;
                        }
                        if (parent.closest('#loading-bar, script, style')) {
                            return NodeFilter.FILTER_REJECT;
                        }
                        return node.nodeValue && node.nodeValue.trim().length > 0
                            ? NodeFilter.FILTER_ACCEPT
                            : NodeFilter.FILTER_SKIP;
                    }
                }
            );

            const nodesToTranslate = [];
            while (walker.nextNode()) {
                nodesToTranslate.push(walker.currentNode);
            }

            for (let i = 0; i < nodesToTranslate.length; i++) {
                const node = nodesToTranslate[i];
                const orig = node.nodeValue.trim();
                if (this.dict[orig]) {
                    // Cache original in parent element if not cached
                    if (!node.parentElement.hasAttribute('data-i18n-orig')) {
                        node.parentElement.setAttribute('data-i18n-orig', orig);
                    }
                    node.nodeValue = node.nodeValue.replace(orig, this.dict[orig]);
                }
            }

            // Also translate placeholders
            const inputs = container.querySelectorAll('input[placeholder], textarea[placeholder]');
            inputs.forEach(inp => {
                const ph = inp.getAttribute('placeholder');
                if (ph && this.dict[ph.trim()]) {
                    if (!inp.hasAttribute('data-ph-orig')) {
                        inp.setAttribute('data-ph-orig', ph);
                    }
                    inp.setAttribute('placeholder', this.dict[ph.trim()]);
                }
            });
        }
    };
})();
