/* ========================================
   家庭说明书 — 搜索 + 折叠章节 + 图片灯箱
   详情页：段内全文搜索 + 跳转展开
   其他页：产品元数据搜索
   ======================================== */

(function () {
    var searchInput = document.getElementById('search-input');
    var searchResults = document.getElementById('search-results');
    var rootMeta = document.querySelector('meta[name="root"]');
    var ROOT = rootMeta ? rootMeta.content : './';

    // 判断当前页面类型
    var isDetailPage = !!(window.__MANUAL_SECTIONS__);
    var sectionData = window.__MANUAL_SECTIONS__ || {};
    var metadataIndex = [];
    var loaded = false;

    // === 加载 ===
    if (isDetailPage) {
        loaded = true;
        searchInput.placeholder = '搜索本说明书内容…';
    } else {
        fetch(ROOT + 'search-index.json')
            .then(function (res) { return res.json(); })
            .then(function (data) {
                metadataIndex = data;
                loaded = true;
            })
            .catch(function () {});
    }

    // === 输入防抖 ===
    var timer = null;
    searchInput.addEventListener('input', function () {
        clearTimeout(timer);
        var q = this.value.trim();
        if (!q) {
            searchResults.classList.remove('active');
            searchResults.innerHTML = '';
            clearHighlights();
            return;
        }
        timer = setTimeout(function () { doSearch(q); }, 200);
    });

    // === 点击外部关闭 ===
    document.addEventListener('click', function (e) {
        if (!searchResults.contains(e.target) && e.target !== searchInput) {
            searchResults.classList.remove('active');
        }
    });

    // === 聚焦重新显示 ===
    searchInput.addEventListener('focus', function () {
        if (this.value.trim() && searchResults.innerHTML) {
            searchResults.classList.add('active');
        }
    });

    // === 键盘导航 ===
    var selectedIdx = -1;
    searchInput.addEventListener('keydown', function (e) {
        var items = searchResults.querySelectorAll('.search-result-item');
        if (e.key === 'ArrowDown') { e.preventDefault(); selectedIdx = Math.min(selectedIdx + 1, items.length - 1); updateSelection(items); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); selectedIdx = Math.max(selectedIdx - 1, 0); updateSelection(items); }
        else if (e.key === 'Enter' && selectedIdx >= 0 && items[selectedIdx]) { items[selectedIdx].click(); }
    });

    function updateSelection(items) {
        items.forEach(function (el, i) { el.classList.toggle('selected', i === selectedIdx); });
    }

    // === 核心搜索 ===
    function doSearch(query) {
        if (!loaded) { searchResults.innerHTML = '<div class="search-no-result">搜索索引加载中…</div>'; searchResults.classList.add('active'); return; }
        selectedIdx = -1;

        if (isDetailPage) {
            searchInSections(query);
        } else {
            searchMetadata(query);
        }
    }

    // --- 详情页：段内搜索 ---
    function searchInSections(query) {
        var q = query.toLowerCase();
        var results = [];

        Object.keys(sectionData).forEach(function (sid) {
            var sec = sectionData[sid];
            var text = (sec.title + ' ' + sec.text).toLowerCase();
            var idx = text.indexOf(q);
            if (idx >= 0) {
                results.push({ section: sid, title: sec.title, text: sec.text, idx: idx });
            }
        });

        if (!results.length) {
            searchResults.innerHTML = '<div class="search-no-result">本页未找到相关内容</div>';
            searchResults.classList.add('active');
            clearHighlights();
            return;
        }

        renderSectionResults(results, query);
    }

    function renderSectionResults(items, query) {
        searchResults.innerHTML = '';
        var q = query.toLowerCase();

        items.forEach(function (item) {
            var el = document.createElement('div');
            el.className = 'search-result-item section-result';
            el.setAttribute('data-section', item.section);

            // 在 text 中找匹配片段
            var txt = item.text;
            var idx = txt.toLowerCase().indexOf(q);
            var start = Math.max(0, idx - 20);
            var end = Math.min(txt.length, idx + query.length + 30);
            var snippet = (start > 0 ? '…' : '') + escapeHtml(txt.substring(start, end)) + (end < txt.length ? '…' : '');
            snippet = snippet.replace(new RegExp(escapeRegex(query), 'gi'), '<mark>$&</mark>');

            el.innerHTML = '<div class="search-result-title">' + escapeHtml(item.title) + '</div>' +
                '<div class="search-result-snippet">' + snippet + '</div>';

            el.addEventListener('click', function () {
                expandAndScroll(item.section, query);
                searchResults.classList.remove('active');
            });

            searchResults.appendChild(el);
        });

        searchResults.classList.add('active');
    }

    function expandAndScroll(sectionId, query) {
        // 找到对应 <details> 并展开
        var section = document.querySelector('.collapsible-section[data-section="' + sectionId + '"]');
        if (!section) return;

        var details = section.querySelector('details');
        if (details && !details.open) {
            details.open = true;
        }

        // 滚动到该章节
        setTimeout(function () {
            section.scrollIntoView({ behavior: 'smooth', block: 'start' });
            // 高亮匹配文字
            highlightInSection(section, query);
        }, 150);
    }

    function highlightInSection(section, query) {
        clearHighlights();
        var body = section.querySelector('.section-body');
        if (!body) return;
        var regex = new RegExp('(' + escapeRegex(query) + ')', 'gi');
        body.innerHTML = body.innerHTML.replace(regex, '<mark class="search-highlight">$1</mark>');
    }

    function clearHighlights() {
        var marks = document.querySelectorAll('.section-body .search-highlight');
        marks.forEach(function (m) {
            var parent = m.parentNode;
            parent.replaceChild(document.createTextNode(m.textContent), m);
            parent.normalize();
        });
    }

    // --- 非详情页：元数据搜索 ---
    function searchMetadata(query) {
        var q = query.toLowerCase();
        var results = [];

        metadataIndex.forEach(function (m) {
            var score = 0;
            if (m.title.toLowerCase().indexOf(q) >= 0) score += 100;
            if (m.brand && m.brand.toLowerCase().indexOf(q) >= 0) score += 50;
            if (m.type && m.type.toLowerCase().indexOf(q) >= 0) score += 50;
            if (m.category.toLowerCase().indexOf(q) >= 0) score += 30;
            if (score > 0) results.push({ manual: m, score: score });
        });

        results.sort(function (a, b) { return b.score - a.score; });
        results = results.slice(0, 15);

        if (!results.length) {
            searchResults.innerHTML = '<div class="search-no-result">未找到相关内容，换个关键词试试</div>';
            searchResults.classList.add('active');
            return;
        }

        searchResults.innerHTML = '';
        results.forEach(function (r) {
            var m = r.manual;
            var el = document.createElement('a');
            el.className = 'search-result-item';
            el.href = ROOT + m.path + '/index.html';

            var typeTag = m.type ? '<span class="tag tag-type">' + escapeHtml(m.type) + '</span>' : '';
            var brandTag = m.brand ? '<span class="tag tag-brand">' + escapeHtml(m.brand) + '</span>' : '';

            el.innerHTML = '<div class="search-result-title">' + escapeHtml(m.title) + '</div>' +
                '<div class="search-result-meta">' + typeTag + ' ' + brandTag + ' · ' + escapeHtml(m.category) + '</div>';

            searchResults.appendChild(el);
        });

        searchResults.classList.add('active');
    }

    // === 折叠章节：TOC 点击展开 ===
    document.addEventListener('click', function (e) {
        var link = e.target.closest('.toc-list a');
        if (!link) return;
        var href = link.getAttribute('href');
        if (!href || !href.startsWith('#')) return;
        var anchor = href.substring(1);
        var span = document.getElementById(anchor);
        if (!span) return;
        var section = span.closest('.collapsible-section');
        if (!section) return;
        var details = section.querySelector('details');
        if (details && !details.open) {
            details.open = true;
        }
        setTimeout(function () {
            span.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    });

    // === 工具函数 ===
    function escapeHtml(text) {
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function escapeRegex(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
})();

/* ========================================
   图片灯箱
   ======================================== */
(function () {
    var overlay = document.createElement('div');
    overlay.className = 'lightbox-overlay';
    overlay.innerHTML = '<button class="lightbox-close">&times;</button><img src="" alt="">';
    document.body.appendChild(overlay);

    var img = overlay.querySelector('img');
    var closeBtn = overlay.querySelector('.lightbox-close');

    function close() { overlay.classList.remove('active'); img.src = ''; }
    overlay.addEventListener('click', function (e) { if (e.target === overlay || e.target === closeBtn) close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });

    function bindImages() {
        var content = document.querySelector('.detail-content');
        if (!content) return;
        content.querySelectorAll('img').forEach(function (el) {
            if (el.closest('.lightbox-overlay')) return;
            if (el._lightboxBound) return;
            el._lightboxBound = true;
            el.addEventListener('click', function () { img.src = el.src; overlay.classList.add('active'); });
        });
    }

    bindImages();
    if (window.MutationObserver) {
        new MutationObserver(bindImages).observe(document.body, { childList: true, subtree: true });
    }
})();
