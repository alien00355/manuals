/* ========================================
   家庭说明书 — 纯前端搜索（零外部依赖）
   ======================================== */

(function () {
    var searchInput = document.getElementById('search-input');
    var searchResults = document.getElementById('search-results');

    // 从 meta 标签读取网站根路径
    var rootMeta = document.querySelector('meta[name="root"]');
    var ROOT = rootMeta ? rootMeta.content : './';

    // 搜索数据
    var manuals = [];
    var loaded = false;

    // --- 加载搜索索引 ---
    fetch(ROOT + 'search-index.json')
        .then(function (res) { return res.json(); })
        .then(function (data) {
            manuals = data;
            loaded = true;
            console.log('搜索索引已加载，共 ' + manuals.length + ' 本说明书');
        })
        .catch(function (err) {
            console.error('搜索索引加载失败:', err);
        });

    // --- 输入防抖 ---
    var timer = null;
    searchInput.addEventListener('input', function () {
        clearTimeout(timer);
        var q = this.value.trim();
        if (!q) {
            searchResults.classList.remove('active');
            searchResults.innerHTML = '';
            return;
        }
        timer = setTimeout(function () { doSearch(q); }, 200);
    });

    // --- 点击外部关闭 ---
    document.addEventListener('click', function (e) {
        if (!searchResults.contains(e.target) && e.target !== searchInput) {
            searchResults.classList.remove('active');
        }
    });

    // --- 聚焦时重新显示 ---
    searchInput.addEventListener('focus', function () {
        if (this.value.trim() && searchResults.innerHTML) {
            searchResults.classList.add('active');
        }
    });

    // --- 键盘导航 ---
    var selectedIdx = -1;
    searchInput.addEventListener('keydown', function (e) {
        var items = searchResults.querySelectorAll('.search-result-item');
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIdx = Math.min(selectedIdx + 1, items.length - 1);
            updateSelection(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIdx = Math.max(selectedIdx - 1, 0);
            updateSelection(items);
        } else if (e.key === 'Enter') {
            if (selectedIdx >= 0 && items[selectedIdx]) {
                items[selectedIdx].click();
            }
        }
    });

    function updateSelection(items) {
        items.forEach(function (el, i) {
            if (i === selectedIdx) { el.classList.add('selected'); }
            else { el.classList.remove('selected'); }
        });
    }

    // --- 核心搜索 ---
    function doSearch(query) {
        if (!loaded || !manuals.length) {
            searchResults.innerHTML = '<div class="search-no-result">搜索索引加载中…</div>';
            searchResults.classList.add('active');
            return;
        }

        var q = query.toLowerCase();
        var results = [];

        manuals.forEach(function (m) {
            var score = 0;
            var matchField = '';

            // 标题匹配（权重最高）
            if (m.title.toLowerCase().indexOf(q) >= 0) {
                score += 100;
                matchField = 'title';
            }
            // 品牌匹配
            if (m.brand && m.brand.toLowerCase().indexOf(q) >= 0) {
                score += 50;
                if (!matchField) matchField = 'brand';
            }
            // 类型匹配
            if (m.type && m.type.toLowerCase().indexOf(q) >= 0) {
                score += 50;
                if (!matchField) matchField = 'type';
            }
            // 正文匹配
            var contentIdx = m.content.toLowerCase().indexOf(q);
            if (contentIdx >= 0) {
                score += 10;
                if (!matchField) matchField = 'content';
            }

            if (score > 0) {
                results.push({
                    manual: m,
                    score: score,
                    contentIdx: contentIdx,
                });
            }
        });

        // 按得分排序
        results.sort(function (a, b) { return b.score - a.score; });

        renderResults(results.slice(0, 15), query);
    }

    // --- 渲染结果 ---
    function renderResults(items, query) {
        searchResults.innerHTML = '';

        if (!items.length) {
            searchResults.innerHTML = '<div class="search-no-result">未找到相关内容，换个关键词试试</div>';
            searchResults.classList.add('active');
            return;
        }

        items.forEach(function (item) {
            var m = item.manual;
            var el = document.createElement('a');
            el.className = 'search-result-item';
            el.href = ROOT + m.path + '/index.html';

            // 生成内容片段
            var snippet = '';
            if (item.contentIdx >= 0 && m.content) {
                var start = Math.max(0, item.contentIdx - 25);
                var end = Math.min(m.content.length, item.contentIdx + query.length + 40);
                snippet = (start > 0 ? '…' : '') +
                    escapeHtml(m.content.substring(start, end)).replace(
                        new RegExp(escapeRegex(query), 'gi'),
                        '<mark>$&</mark>'
                    ) +
                    (end < m.content.length ? '…' : '');
            } else if (m.content) {
                snippet = escapeHtml(m.content.substring(0, 80)) + '…';
            }

            var typeTag = m.type ? '<span class="tag tag-type">' + escapeHtml(m.type) + '</span>' : '';
            var brandTag = m.brand ? '<span class="tag tag-brand">' + escapeHtml(m.brand) + '</span>' : '';

            el.innerHTML =
                '<div class="search-result-title">' + escapeHtml(m.title) + '</div>' +
                (snippet ? '<div class="search-result-snippet">' + snippet + '</div>' : '') +
                '<div class="search-result-meta">' + typeTag + ' ' + brandTag + ' · ' + escapeHtml(m.category) + '</div>';

            searchResults.appendChild(el);
        });

        searchResults.classList.add('active');
    }

    // --- 工具函数 ---
    function escapeHtml(text) {
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function escapeRegex(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
})();
