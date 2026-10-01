// ============================================================
    // BATCH 7H — REAL PROGRESS TRACKER + ASYNC FLOW
    // ============================================================

    // ----- H3: YIELD TO BROWSER -----
    function yieldToBrowser() {
      // requestAnimationFrame may not fire while the document is backgrounded
      // or under mobile browser throttling. Keep a timer fallback so the
      // initialization pipeline can never remain stuck on the reveal step.
      return new Promise(resolve => {
        let settled = false;
        const finish = () => {
          if (settled) return;
          settled = true;
          resolve();
        };
        if (typeof requestAnimationFrame === "function") {
          requestAnimationFrame(finish);
        }
        setTimeout(finish, 50);
      });
    }

    async function processWithYield(items, onProgress) {
      const total = items.length;
      if (total === 0) return;
      const chunkSize = Math.max(1, Math.floor(total / 20));
      for (let i = 0; i < total; i++) {
        try { await items[i](); } catch (err) { console.error("[GW] task error:", err); }
        if ((i + 1) % chunkSize === 0 || i === total - 1) {
          onProgress(i + 1, total);
          await yieldToBrowser();
        }
      }
    }

    // ----- H2: PROGRESS TRACKER -----
    const Progress = (function() {
      let tasks = [];
      let fill, percent, textEl;
      const MIN_DISPLAY_MS = 400;
      let startTime = 0;

      function init(steps) {
        fill = document.getElementById("gw-loader-fill");
        percent = document.getElementById("gw-loader-percent");
        textEl = document.getElementById("gw-loader-text");
        tasks = steps.map(s => ({ ...s, done: false }));
        startTime = performance.now();
        render();
      }

      function setTask(name, isDone) {
        const task = tasks.find(t => t.name === name);
        if (!task) return;
        task.done = isDone;
        render();
      }

      function render() {
        if (!fill || !percent || !textEl) return;
        let total = 0, sum = 0;
        tasks.forEach(t => {
          total += t.weight;
          if (t.done) sum += t.weight;
        });
        const pct = total > 0 ? Math.min(100, (sum / total) * 100) : 0;
        fill.style.width = pct + "%";
        percent.textContent = Math.round(pct) + "%";
        const active = tasks.find(t => !t.done);
        if (active) textEl.textContent = active.label;
      }

      function complete() {
        tasks.forEach(t => t.done = true);
        render();
        if (textEl) textEl.textContent = "Siap!";
      }

      async function dismiss() {
        const elapsed = performance.now() - startTime;
        if (elapsed < MIN_DISPLAY_MS) {
          await new Promise(r => setTimeout(r, MIN_DISPLAY_MS - elapsed));
        }
        complete();
        const loader = document.getElementById("gw-loader");
        if (!loader) return;
        loader.classList.add("hidden");
        setTimeout(() => loader.classList.add("fade-complete"), 450);
      }

      return { init, setTask, complete, dismiss };
    })();

    // ----- SAFE STEP -----
    async function safeStep(name, fn) {
      try {
        await fn();
      } catch (err) {
        console.error("[GW] Step failed:", name, err);
      }
      Progress.setTask(name, true);
    }

    // ============================================================
    // LOADER WATCHDOG — never leave the viewer behind at 95%.
    // ============================================================
    (function installLoaderWatchdog() {
      const MAX_WAIT_MS = 12000;
      const forceReveal = (reason) => {
        const loader = document.getElementById("gw-loader");
        if (!loader || loader.classList.contains("fade-complete")) return;
        console.warn("[GW] Loader watchdog reveal:", reason);
        const fill = document.getElementById("gw-loader-fill");
        const percent = document.getElementById("gw-loader-percent");
        const text = document.getElementById("gw-loader-text");
        if (fill) fill.style.width = "100%";
        if (percent) percent.textContent = "100%";
        if (text) text.textContent = "Siap";
        loader.classList.add("hidden");
        setTimeout(() => loader.classList.add("fade-complete"), 450);
      };
      window.setTimeout(() => forceReveal("initialization timeout"), MAX_WAIT_MS);
      window.addEventListener("error", (event) => {
        if (Date.now()) console.error("[GW] Viewer runtime error:", event.error || event.message);
      });
      window.addEventListener("unhandledrejection", (event) => {
        console.error("[GW] Viewer promise error:", event.reason);
      });
    })();

    // ============================================================
    // MAIN FLOW
    // ============================================================
    document.addEventListener("DOMContentLoaded", async () => {
      const STORAGE_KEY_THEME = "gw-theme";
      const STORAGE_KEY_SCROLL = "gw-scroll-" + (document.getElementById("chat-title")?.textContent || "").trim();

      // Theme icon restore (anti-FOUC udah handle class di <head>)
      const savedTheme = localStorage.getItem(STORAGE_KEY_THEME);
      if (savedTheme !== "light" && savedTheme !== "dark") {
        const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        document.documentElement.setAttribute("data-theme", prefersDark ? "dark" : "light");
      }
      if (savedTheme === "light") {
        const tt = document.getElementById("theme-toggle");
        if (tt) tt.textContent = "☀️";
      }

      // Init progress tracker
      Progress.init([
        { name: "parse-md",   weight: 35, label: "Render markdown..." },
        { name: "highlight",  weight: 15, label: "Highlight code..." },
        { name: "katex",      weight: 10, label: "Render math..." },
        { name: "sidebar",    weight: 15, label: "Bangun sidebar..." },
        { name: "right-rail", weight: 10, label: "Bangun navigasi user..." },
        { name: "stats",      weight: 5,  label: "Hitung statistik..." },
        { name: "observers",  weight: 5,  label: "Setup observer..." },
        { name: "reveal",     weight: 5,  label: "Menyiapkan viewer..." },
      ]);

      // Marked config
      if (typeof marked !== "undefined") marked.use({ gfm: true, breaks: true });

      // ============================================================
      // STEP 1 — RENDER MARKDOWN
      // ============================================================
      await safeStep("parse-md", async () => {
        const bubbles = Array.from(document.querySelectorAll(".markdown-body"));
        const tasks = bubbles.map(el => () => {
          const raw = el.getAttribute("data-raw");
          if (!raw) return;
          const decoder = document.createElement("textarea");
          decoder.innerHTML = raw;
          const decoded = decoder.value;
          if (typeof marked !== "undefined") el.innerHTML = marked.parse(decoded);
          else el.textContent = decoded;
        });
        await processWithYield(tasks, () => {});
      });

      // ============================================================
      // STEP 2 — CODE BLOCKS (DECORATE FIRST, HIGHLIGHT OPTIONAL)
      // ============================================================
      // Code controls must work even when highlight.js fails to load.
      await safeStep("highlight", async () => {
        const codeBlocks = Array.from(document.querySelectorAll(".markdown-body pre code"));
        const tasks = codeBlocks.map(block => () => {
          const pre = block.parentElement;
          if (!pre) return;

          if (typeof hljs !== "undefined") {
            try { hljs.highlightElement(block); } catch (e) {}
          }

          if (!pre.querySelector(":scope > .code-header")) {
            const langMatch = (block.className || "").match(/(?:language-|lang-)([A-Za-z0-9_+-]+)/);
            const lang = langMatch ? langMatch[1] : "text";
            const header = document.createElement("div");
            header.className = "code-header";
            header.innerHTML = `
              <span class="code-lang">${escapeHtml(lang)}</span>
              <span class="code-actions">
                <button type="button" class="code-copy-btn" data-code-action="copy" title="Copy code">Copy</button>
                <button type="button" data-code-action="fullscreen" title="Fullscreen">⤢</button>
                <button type="button" data-code-action="menu" title="Menu">⋯</button>
              </span>`;
            pre.insertBefore(header, block);
          }

          // Inner collapse is independent from the outer message collapse.
          const lineCount = (block.textContent || "").replace(/\n$/, "").split("\n").length;
          const existingWrap = pre.parentElement?.classList.contains("code-collapse-wrap")
            ? pre.parentElement : null;
          if (lineCount > 10 && !existingWrap && !pre.dataset.innerCollapseReady) {
            const wrap = document.createElement("div");
            wrap.className = "code-collapse-wrap";
            wrap.dataset.innerCollapse = "true";
            wrap.classList.add("is-collapsed");
            pre.parentNode.insertBefore(wrap, pre);
            wrap.appendChild(pre);
            pre.classList.add("code-collapsed");
            pre.dataset.innerCollapseReady = "true";

            const all = document.createElement("button");
            all.className = "code-view-all";
            all.type = "button";
            all.setAttribute("aria-expanded", "false");
            all.innerHTML = `<span>View all</span><span class="code-line-count">${lineCount} lines</span>`;
            all.addEventListener("click", (event) => {
              event.stopPropagation();
              const collapsed = pre.classList.toggle("code-collapsed");
              wrap.classList.toggle("is-collapsed", collapsed);
              all.setAttribute("aria-expanded", String(!collapsed));
              all.querySelector("span:first-child").textContent = collapsed ? "View all" : "Collapse";
            });
            wrap.appendChild(all);
          }
        });
        await processWithYield(tasks, () => {});
      });

      // ============================================================
      // STEP 3 — KATEX
      // ============================================================
      await safeStep("katex", async () => {
        if (typeof renderMathInElement === "undefined") return;
        const bodies = Array.from(document.querySelectorAll(".markdown-body"));
        const tasks = bodies.map(el => () => {
          try {
            renderMathInElement(el, {
              delimiters: [
                { left: "$$", right: "$$", display: true },
                { left: "\\[", right: "\\]", display: true },
                { left: "$", right: "$", display: false },
                { left: "\\(", right: "\\)", display: false }
              ],
              throwOnError: false,
              errorColor: "#f87171"
            });
          } catch (e) {}
        });
        await processWithYield(tasks, () => {});
      });

      // ============================================================
      // DOM REFS (dibutuhin buat step berikutnya)
      // ============================================================
      const sidebar = document.getElementById("sidebar");
      const sidebarOverlay = document.getElementById("sidebar-overlay");
      const sidebarList = document.getElementById("sidebar-list");
      const sidebarCloseBtn = document.getElementById("sidebar-close-btn");
      const sidebarToggle = document.getElementById("sidebar-toggle");
      const chatContainer = document.getElementById("chat-container");

      // CRITICAL UI CONTROLS: bind before any async/yielding initialization.
      // A slow import, network request, or optional vendor script must never
      // make the header controls inert. These handlers are intentionally
      // centralized so the same click cannot be bound twice.
      const helpOverlayEarly = document.getElementById("help-modal-overlay");
      const helpToggleEarly = document.getElementById("help-toggle");
      const helpCloseEarly = document.getElementById("help-modal-close");
      const headerMenuToggleEarly = document.getElementById("header-menu-toggle");
      const headerMenuDropdownEarly = document.getElementById("header-menu-dropdown");

      function closeHeaderMenuEarly() {
        headerMenuDropdownEarly?.classList.remove("visible");
        headerMenuToggleEarly?.classList.remove("active");
      }
      function openHelpEarly() {
        helpOverlayEarly?.classList.add("visible");
        document.body.style.overflow = "hidden";
      }
      function closeHelpEarly() {
        helpOverlayEarly?.classList.remove("visible");
        document.body.style.overflow = "";
      }

      sidebarToggle?.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        if (sidebar?.classList.contains("collapsed")) openSidebar();
        else closeSidebar();
      });
      sidebarOverlay?.addEventListener("click", closeSidebar);
      sidebarCloseBtn?.addEventListener("click", closeSidebar);

      helpToggleEarly?.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        if (helpOverlayEarly?.classList.contains("visible")) closeHelpEarly();
        else openHelpEarly();
      });
      helpCloseEarly?.addEventListener("click", closeHelpEarly);
      helpOverlayEarly?.addEventListener("click", (event) => {
        if (event.target === helpOverlayEarly) closeHelpEarly();
      });

      headerMenuToggleEarly?.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        const opening = !headerMenuDropdownEarly?.classList.contains("visible");
        closeHeaderMenuEarly();
        if (opening) {
          headerMenuDropdownEarly?.classList.add("visible");
          headerMenuToggleEarly?.classList.add("active");
        }
      });
      headerMenuDropdownEarly?.addEventListener("click", event => event.stopPropagation());
      document.addEventListener("click", closeHeaderMenuEarly);

      function openSidebar() {
        sidebar?.classList.remove("collapsed");
        if (window.innerWidth <= 768) sidebarOverlay?.classList.add("visible");
        const rr = document.getElementById("right-rail");
        if (rr && !rr.classList.contains("collapsed")) {
          rr.classList.add("collapsed");
          document.body.classList.add("right-rail-collapsed");
          document.getElementById("right-rail-overlay")?.classList.remove("visible");
        }
      }

      function closeSidebar() {
        sidebar?.classList.add("collapsed");
        sidebarOverlay?.classList.remove("visible");
      }

      // ============================================================
      // STEP 4 — BUILD SIDEBAR
      // ============================================================
      function getDateGroup(mtime) {
        const now = new Date();
        const d = new Date(mtime * 1000);
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const target = new Date(d.getFullYear(), d.getMonth(), d.getDate());
        const diffDays = Math.floor((today - target) / 86400000);
        if (diffDays <= 0) return "Hari Ini";
        if (diffDays === 1) return "Kemarin";
        if (diffDays <= 7) return "7 Hari Terakhir";
        if (diffDays <= 30) return "30 Hari Terakhir";
        return "Lebih Lama";
      }

      const DATE_GROUP_ORDER = ["Hari Ini", "Kemarin", "7 Hari Terakhir", "30 Hari Terakhir", "Lebih Lama"];

      function detectCurrentId() {
        const parts = window.location.pathname.split("/").filter(Boolean);
        if (parts.length === 0) return "";
        const historyIdx = parts.indexOf("history");
        if (historyIdx !== -1 && parts.length > historyIdx + 1) {
          return parts[historyIdx + 1] || "";
        }
        if (parts[parts.length - 1] === "index.html") {
          return parts[parts.length - 2] || "";
        }
        return parts[parts.length - 1] || "";
      }

      let sidebarDataItems = [];

      await safeStep("sidebar", async () => {
        const currentId = detectCurrentId();
        const isMobile = window.matchMedia("(max-width: 768px)").matches;

        try {
          const r = await fetch("../../index.json", { cache: "no-store" });
          if (!r.ok) throw new Error("index.json not found");
          const data = await r.json();

          if (!data || !Array.isArray(data.items) || data.items.length === 0) {
            if (!isMobile) sidebar.style.display = "none";
            return;
          }

          if (data.items.length <= 1) {
            sidebar.style.display = "none";
            return;
          }

          sidebarDataItems = data.items;

          const groups = {};
          data.items.forEach(item => {
            const g = getDateGroup(item.mtime || 0);
            if (!groups[g]) groups[g] = [];
            groups[g].push(item);
          });

          sidebarList.innerHTML = "";
          const tasks = [];
          DATE_GROUP_ORDER.forEach(groupName => {
            const items = groups[groupName];
            if (!items || items.length === 0) return;

            tasks.push(() => {
              const section = document.createElement("div");
              section.className = "sidebar-section";
              const label = document.createElement("div");
              label.className = "sidebar-section-label";
              label.textContent = groupName;
              section.appendChild(label);

              items.forEach(item => {
                const isActive = item.id === currentId;
                const el = document.createElement("div");
                el.className = "sidebar-item" + (isActive ? " active" : "");

                const itemType = item.type || "chat";
                const typeEmoji = { chat: "💬", ebook: "📖", comic: "🎨" }[itemType] || "📄";
                let metaInfo;
                if (itemType === "chat") {
                  metaInfo = item.msg_count ? `${item.msg_count} pesan` : `${item.size_kb} KB`;
                } else {
                  metaInfo = item.pages ? `${item.pages} halaman` : `${item.size_kb} KB`;
                }

                el.innerHTML = `
                  <span class="sidebar-item-title" title="${escapeHtml(item.title)}">${typeEmoji} ${escapeHtml(item.title)}</span>
                  <span class="sidebar-item-meta">${metaInfo}</span>
                `;
                el.addEventListener("click", () => {
                  if (isActive) return;
                  const folder = item.folder || ("history/" + item.id);
                  window.location.href = "../../" + folder + "/";
                });
                section.appendChild(el);
              });

              sidebarList.appendChild(section);
            });
          });

          await processWithYield(tasks, () => {});
        } catch (e) {
          if (!isMobile) sidebar.style.display = "none";
        }
      });

      // ============================================================
      // STEP 5 — BUILD RIGHT RAIL
      // ============================================================
      const rightRail = document.getElementById("right-rail");
      const rightRailList = document.getElementById("right-rail-list");
      const rightRailClose = document.getElementById("right-rail-close");
      const rightRailOverlay = document.getElementById("right-rail-overlay");
      const rightRailToggle = document.getElementById("right-rail-toggle");

      function openRightRail() {
        rightRail.classList.remove("collapsed");
        document.body.classList.remove("right-rail-collapsed");
        if (window.innerWidth <= 1024) rightRailOverlay?.classList.add("visible");
        const sb = document.getElementById("sidebar");
        if (sb && !sb.classList.contains("collapsed")) {
          sb.classList.add("collapsed");
          const sbOverlay = document.getElementById("sidebar-overlay");
          if (sbOverlay) sbOverlay.classList.remove("visible");
        }
      }

      function closeRightRail() {
        rightRail.classList.add("collapsed");
        document.body.classList.add("right-rail-collapsed");
        rightRailOverlay?.classList.remove("visible");
      }

      function toggleRightRail() {
        if (rightRail.classList.contains("collapsed")) openRightRail();
        else closeRightRail();
      }

      rightRailClose?.addEventListener("click", closeRightRail);
      rightRailOverlay?.addEventListener("click", closeRightRail);
      rightRailToggle?.addEventListener("click", toggleRightRail);

      await safeStep("right-rail", async () => {
        const userRows = Array.from(document.querySelectorAll('.message-row[data-role="user"]'));
        if (userRows.length === 0) {
          rightRailList.innerHTML = '<div style="padding: 12px; color: var(--text-muted); font-size: 0.78rem; text-align: center;">Belum ada pesan user.</div>';
          return;
        }
        rightRailList.innerHTML = "";

        const tasks = userRows.map((row, i) => () => {
          const bubble = row.querySelector(".bubble");
          const raw = bubble?.getAttribute("data-raw") || "";
          const decoder = document.createElement("textarea");
          decoder.innerHTML = raw;
          const text = decoder.value.replace(/\s+/g, " ").trim();
          const item = document.createElement("div");
          item.className = "user-nav-item";
          item.dataset.targetIndex = row.getAttribute("data-msg-index");
          item.innerHTML = `
            <span class="user-nav-index">${String(i + 1).padStart(2, "0")}</span>
            <span class="user-nav-text">${escapeHtml(text.slice(0, 120))}${text.length > 120 ? "…" : ""}</span>
          `;
          item.addEventListener("click", () => {
            const target = document.querySelector(`.message-row[data-msg-index="${item.dataset.targetIndex}"]`);
            if (target) {
              target.scrollIntoView({ behavior: "smooth", block: "start" });
              document.querySelectorAll(".user-nav-item").forEach(el => el.classList.remove("active"));
              item.classList.add("active");
              if (window.innerWidth <= 1024) closeRightRail();
            }
          });
          rightRailList.appendChild(item);
        });

        await processWithYield(tasks, () => {});
      });

      function updateActiveUserNav() {
        const userRows = Array.from(document.querySelectorAll('.message-row[data-role="user"]'));
        if (userRows.length === 0) return;
        const scrollTop = chatContainer.scrollTop;
        const viewportMid = scrollTop + chatContainer.clientHeight / 3;
        let active = null;
        for (const row of userRows) {
          if (row.offsetTop <= viewportMid) active = row;
          else break;
        }
        document.querySelectorAll(".user-nav-item").forEach(el => el.classList.remove("active"));
        if (active) {
          const idx = active.getAttribute("data-msg-index");
          const navItem = document.querySelector(`.user-nav-item[data-target-index="${idx}"]`);
          if (navItem) {
            navItem.classList.add("active");
            navItem.scrollIntoView({ block: "nearest", behavior: "smooth" });
          }
        }
      }

      // ============================================================
      // STEP 6 — COMPUTE STATS
      // ============================================================
      await safeStep("stats", async () => {
        const bubbles = document.querySelectorAll(".bubble");
        let totalChars = 0;
        bubbles.forEach(b => { totalChars += (b.getAttribute("data-raw") || "").length; });

        const statChars = document.getElementById("stat-chars");
        const statTokens = document.getElementById("stat-tokens");
        const statDuration = document.getElementById("stat-duration");

        if (statChars) {
          statChars.textContent = totalChars >= 1000
            ? (totalChars / 1000).toFixed(1) + "K"
            : totalChars.toLocaleString();
        }
        if (statTokens) {
          const t = Math.round(totalChars / 4);
          statTokens.textContent = t >= 1000
            ? (t / 1000).toFixed(1) + "K"
            : t.toLocaleString();
        }
        if (statDuration) {
          const timeEls = document.querySelectorAll(".meta-time");
          if (timeEls.length >= 2) {
            const first = timeEls[0].textContent.trim();
            const last = timeEls[timeEls.length - 1].textContent.trim();
            statDuration.textContent = `${first}→${last}`;
          } else {
            statDuration.textContent = "—";
          }
        }
      });

      // ============================================================
      // STEP 7 — SETUP OBSERVERS + HANDLERS
      // ============================================================
      await safeStep("observers", async () => {
        // Collapse toggle
        let collapsedCount = 0;
        document.querySelectorAll(".bubble.collapsible").forEach(bubble => {
          collapsedCount++;
          const toggle = document.createElement("button");
          toggle.className = "collapse-toggle";
          toggle.type = "button";
          toggle.innerHTML = '<span class="label">Tampilkan semua</span> <span class="icon">▼</span>';
          toggle.addEventListener("click", () => {
            const isExpanded = bubble.classList.toggle("expanded");
            toggle.classList.toggle("expanded", isExpanded);
            toggle.querySelector(".label").textContent = isExpanded ? "Sembunyikan" : "Tampilkan semua";
            if (!isExpanded) bubble.scrollIntoView({ behavior: "smooth", block: "start" });
          });
          bubble.parentElement.appendChild(toggle);
        });

        // Attachment badge
        document.querySelectorAll(".message-row").forEach(row => {
          const bubble = row.querySelector(".bubble");
          const attachmentBoxes = bubble?.querySelectorAll(".attachment-box") || [];
          if (attachmentBoxes.length > 0) {
            const badge = document.createElement("span");
            badge.className = "attachment-badge";
            badge.textContent = `📎 ${attachmentBoxes.length} attachment`;
            const wrapper = row.querySelector(".bubble-wrapper");
            if (wrapper) wrapper.appendChild(badge);
          }
        });

        // Copy msg
        document.querySelectorAll(".copy-msg-btn").forEach(btn => {
          btn.addEventListener("click", (e) => {
            e.stopPropagation();
            const wrapper = btn.closest(".bubble-wrapper");
            const bubble = wrapper?.querySelector(".bubble");
            const raw = bubble ? (bubble.getAttribute("data-raw") || "") : "";
            const decoder = document.createElement("textarea");
            decoder.innerHTML = raw;
            const text = decoder.value;
            navigator.clipboard.writeText(text).then(() => {
              btn.textContent = "✓";
              setTimeout(() => { btn.textContent = "📋"; }, 1500);
            }).catch(() => {
              btn.textContent = "✗";
              setTimeout(() => { btn.textContent = "📋"; }, 1500);
            });
          });
        });

        // Msg menu
        function closeAllMsgMenus() {
          document.querySelectorAll(".msg-menu-dropdown.visible").forEach(d => d.classList.remove("visible"));
          document.querySelectorAll(".msg-menu-btn.active").forEach(b => b.classList.remove("active"));
        }

        document.querySelectorAll(".msg-menu-btn").forEach(btn => {
          btn.addEventListener("click", (e) => {
            e.stopPropagation();
            const dropdown = btn.parentElement.querySelector(".msg-menu-dropdown");
            const isOpen = dropdown.classList.contains("visible");
            closeAllMsgMenus();
            if (!isOpen) {
              const btnRect = btn.getBoundingClientRect();
              const menuWidth = 180;
              const spaceOnRight = window.innerWidth - btnRect.right;
              const spaceOnLeft = btnRect.left;
              dropdown.classList.remove("open-right");
              if (spaceOnRight < menuWidth + 16 && spaceOnLeft > menuWidth + 16) {
                dropdown.classList.add("open-right");
              } else if (spaceOnLeft < menuWidth + 16 && spaceOnRight < menuWidth + 16) {
                if (spaceOnLeft > spaceOnRight) dropdown.classList.add("open-right");
              }
              dropdown.classList.add("visible");
              btn.classList.add("active");
            }
          });
        });

        chatContainer?.addEventListener("scroll", () => closeAllMsgMenus(), { passive: true });
        document.addEventListener("click", closeAllMsgMenus);

        function showToast(msg, type = "success") {
          const toast = document.getElementById("gw-toast");
          if (!toast) return;
          toast.textContent = msg;
          toast.className = "gw-toast visible " + type;
          clearTimeout(toast._timer);
          toast._timer = setTimeout(() => toast.classList.remove("visible"), 2000);
        }

        function downloadAsFile(filename, content) {
          const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          setTimeout(() => URL.revokeObjectURL(url), 1000);
        }

        function getMessageData(btn) {
          const wrapper = btn.closest(".bubble-wrapper");
          const bubble = wrapper?.querySelector(".bubble");
          const row = btn.closest(".message-row");
          if (!bubble || !row) return null;
          const raw = bubble.getAttribute("data-raw") || "";
          const decoder = document.createElement("textarea");
          decoder.innerHTML = raw;
          const text = decoder.value;
          const msgIndex = row.getAttribute("data-msg-index") || "0";
          const role = row.getAttribute("data-role") || "unknown";
          const timestamp = row.querySelector(".meta-time")?.textContent?.trim() || "";
          return { text, msgIndex, role, timestamp, row };
        }

        document.querySelectorAll(".msg-menu-item").forEach(item => {
          item.addEventListener("click", (e) => {
            e.stopPropagation();
            const action = item.getAttribute("data-action");
            const data = getMessageData(item);
            if (!data) return;
            if (action === "copy-md") {
              navigator.clipboard.writeText(data.text).then(() => showToast("✓ Markdown di-copy"))
                .catch(() => showToast("✗ Gagal copy", "error"));
            } else if (action === "save-md") {
              const roleLabel = data.role === "user" ? "user" : "assistant";
              const ts = data.timestamp ? `-${data.timestamp.replace(/[^0-9]/g, "")}` : "";
              const filename = `msg-${String(data.msgIndex).padStart(3, "0")}-${roleLabel}${ts}.md`;
              const header = `# Message #${data.msgIndex} (${roleLabel})\n\n`;
              const meta = data.timestamp ? `> Timestamp: ${data.timestamp}\n\n---\n\n` : "";
              downloadAsFile(filename, header + meta + data.text);
              showToast(`✓ Saved: ${filename}`);
            } else if (action === "copy-link") {
              const url = window.location.origin + window.location.pathname + `#msg-${data.msgIndex}`;
              navigator.clipboard.writeText(url).then(() => showToast("✓ Permalink di-copy"))
                .catch(() => showToast("✗ Gagal copy link", "error"));
            }
            closeAllMsgMenus();
          });
        });

        // Code block actions — fullscreen, copy, menu.
        function getCodeText(pre){ return pre?.querySelector("code")?.innerText || ""; }
        function showCodeFullscreen(pre){
          const overlay=document.createElement("div"); overlay.className="code-fullscreen";
          const lang=pre.querySelector(".code-lang")?.textContent||"code";
          overlay.innerHTML=`<div class="code-fullscreen-header"><strong>${escapeHtml(lang)}</strong><span style="margin-left:auto"></span><button class="header-btn" data-fs-copy>📋</button><button class="header-btn" data-fs-download>💾</button><button class="header-btn" data-fs-close>✕</button></div><pre><code>${escapeHtml(getCodeText(pre))}</code></pre>`;
          document.body.appendChild(overlay);
          overlay.querySelector("[data-fs-copy]").onclick=()=>navigator.clipboard.writeText(getCodeText(pre));
          overlay.querySelector("[data-fs-download]").onclick=()=>downloadAsFile(`${lang.replace(/[^a-z0-9_-]/gi,"_")||"code"}.txt`,getCodeText(pre));
          overlay.querySelector("[data-fs-close]").onclick=()=>overlay.remove();
          const esc=e=>{if(e.key==="Escape"){overlay.remove();document.removeEventListener("keydown",esc);}}; document.addEventListener("keydown",esc);
        }
        document.querySelectorAll(".code-header").forEach(header=>{
          const pre=header.closest("pre") || header.parentElement?.querySelector("pre");
          header.querySelectorAll("[data-code-action]").forEach(btn=>btn.addEventListener("click",e=>{
            e.stopPropagation(); const action=btn.dataset.codeAction;
            if(action==="fullscreen") showCodeFullscreen(pre);
            else if(action==="copy") navigator.clipboard.writeText(getCodeText(pre)).then(()=>showToast("✓ Code di-copy")).catch(()=>showToast("✗ Gagal copy", "error"));
            else if(action==="menu"){
              const menu=document.createElement("div"); menu.className="msg-menu-dropdown visible"; menu.style.position="absolute"; menu.innerHTML='<button class="msg-menu-item" data-cm="download">💾 Download as file</button><button class="msg-menu-item" data-cm="wrap">↔️ Toggle word wrap</button><button class="msg-menu-item" data-cm="select">☑ Select all</button>';
              header.style.position="relative"; header.appendChild(menu);
              menu.addEventListener("click",ev=>{const a=ev.target.closest("[data-cm]")?.dataset.cm;if(a==="download")downloadAsFile("code.txt",getCodeText(pre));if(a==="wrap")pre.style.whiteSpace=pre.style.whiteSpace==="pre-wrap"?"pre":"pre-wrap";if(a==="select"){const r=document.createRange();r.selectNodeContents(pre.querySelector("code"));const sel=getSelection();sel.removeAllRanges();sel.addRange(r);}menu.remove();});
            }
          }));
        });

        // Message actions: TTS, Web Share/copy fallback, local bookmark.
        document.querySelectorAll(".msg-tts-btn").forEach(btn=>btn.addEventListener("click",()=>{const d=getMessageData(btn);if(d&&"speechSynthesis" in window){speechSynthesis.cancel();speechSynthesis.speak(new SpeechSynthesisUtterance(d.text));showToast("🔊 Membacakan pesan");}}));
        document.querySelectorAll(".msg-share-btn").forEach(btn=>btn.addEventListener("click",async()=>{const d=getMessageData(btn);if(!d)return;const url=window.location.origin+window.location.pathname+`#msg-${d.msgIndex}`;if(navigator.share){try{await navigator.share({title:document.title,text:d.text.slice(0,160),url});}catch(e){}}else{await navigator.clipboard.writeText(url);showToast("✓ Link di-copy");}}));
        document.querySelectorAll(".msg-bookmark-btn").forEach(btn=>btn.addEventListener("click",()=>{const d=getMessageData(btn);if(!d)return;const key="gw-bookmarks-"+(document.title||"archive");let list=[];try{list=JSON.parse(localStorage.getItem(key)||"[]");}catch(e){}const id=String(d.msgIndex);if(list.includes(id)){list=list.filter(x=>x!==id);btn.textContent="⭐";showToast("Bookmark dihapus");}else{list.push(id);btn.textContent="★";showToast("✓ Pesan di-bookmark");}localStorage.setItem(key,JSON.stringify(list));}));

        // Scroll fade observers
        const messages = document.querySelectorAll(".message-row");
        const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        if (messages.length > 0 && !prefersReduced && "IntersectionObserver" in window) {
          const viewportHeight = window.innerHeight;
          messages.forEach((msg) => {
            const rect = msg.getBoundingClientRect();
            const isInViewport = rect.top < viewportHeight && rect.bottom > 0;
            if (isInViewport) {
              msg.style.transition = "none";
              msg.classList.add("fade-active");
              requestAnimationFrame(() => {
                requestAnimationFrame(() => { msg.style.transition = ""; });
              });
            }
          });

          const activeObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
              const msg = entry.target;
              if (entry.isIntersecting) {
                msg.classList.remove("fade-dim-above", "fade-dim-below");
                msg.classList.add("fade-active");
              }
            });
          }, { root: chatContainer, rootMargin: "-10% 0px -10% 0px", threshold: 0 });

          const dimObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
              const msg = entry.target;
              if (!entry.isIntersecting) {
                const rect = entry.boundingClientRect;
                if (rect.bottom < 0) {
                  msg.classList.remove("fade-active", "fade-dim-below");
                  msg.classList.add("fade-dim-above");
                } else if (rect.top > 0) {
                  msg.classList.remove("fade-active", "fade-dim-above");
                  msg.classList.add("fade-dim-below");
                }
              }
            });
          }, { root: chatContainer, rootMargin: "50px 0px 50px 0px", threshold: 0 });

          messages.forEach(msg => {
            activeObserver.observe(msg);
            dimObserver.observe(msg);
          });
          window.addEventListener("beforeunload", () => {
            activeObserver.disconnect();
            dimObserver.disconnect();
          });
        } else {
          messages.forEach(msg => msg.classList.add("fade-active"));
        }
      });

      // ============================================================
      // SEARCH
      // ============================================================
      const searchBar = document.getElementById("search-bar");
      const searchInput = document.getElementById("search-input");
      const searchCount = document.getElementById("search-count");
      const searchClearBtn = document.getElementById("search-clear-btn");
      const searchPrevBtn = document.getElementById("search-prev-btn");
      const searchNextBtn = document.getElementById("search-next-btn");
      let searchMatches = [];
      let activeMatchIndex = -1;

      function clearSearch() {
        document.querySelectorAll("mark.search-highlight").forEach(mark => {
          const parent = mark.parentNode;
          parent.replaceChild(document.createTextNode(mark.textContent), mark);
          parent.normalize();
        });
        searchMatches = [];
        activeMatchIndex = -1;
        searchCount.textContent = "";
        searchBar?.classList.remove("searching");
        document.body.classList.remove("searching");
        updateSearchNavButtons();
      }

      function updateSearchNavButtons() {
        const hasMatches = searchMatches.length > 0;
        if (searchPrevBtn) searchPrevBtn.disabled = !hasMatches;
        if (searchNextBtn) searchNextBtn.disabled = !hasMatches;
      }

      function focusMatch(idx) {
        searchMatches.forEach((m, i) => m.classList.toggle("active", i === idx));
        const target = searchMatches[idx];
        if (target) target.scrollIntoView({ behavior: "smooth", block: "center" });
      }

      function doSearch(query) {
        clearSearch();
        if (!query || query.length < 2) return;

        searchBar?.classList.add("searching");
        document.body.classList.add("searching");

        let matcher = null;
        const regexMatch = query.match(/^\/(.+)\/([gimsuy]*)$/);
        if (regexMatch) {
          try { matcher = new RegExp(regexMatch[1], regexMatch[2].includes("g") ? regexMatch[2] : regexMatch[2] + "g"); } catch (e) { matcher = null; }
        }
        const lowerQuery = query.toLowerCase();
        const walker = document.createTreeWalker(chatContainer, NodeFilter.SHOW_TEXT, {
          acceptNode: (node) => {
            if (!node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
            const parent = node.parentElement;
            if (!parent) return NodeFilter.FILTER_REJECT;
            const tag = parent.tagName;
            if (tag === "SCRIPT" || tag === "STYLE" || tag === "BUTTON" || tag === "MARK") return NodeFilter.FILTER_REJECT;
            return NodeFilter.FILTER_ACCEPT;
          }
        });
        const textNodes = [];
        let node;
        while ((node = walker.nextNode())) textNodes.push(node);

        textNodes.forEach(textNode => {
          const text = textNode.nodeValue;
          const frag = document.createDocumentFragment();
          const matches = [];
          if (matcher) {
            matcher.lastIndex = 0; let m;
            while ((m = matcher.exec(text)) !== null) { matches.push({index:m.index,value:m[0]}); if (!matcher.global) break; if (m[0] === "") matcher.lastIndex++; }
          } else {
            const lowerText = text.toLowerCase(); let idx = lowerText.indexOf(lowerQuery);
            while (idx !== -1) { matches.push({index:idx,value:text.slice(idx, idx + query.length)}); idx = lowerText.indexOf(lowerQuery, idx + query.length); }
          }
          if (!matches.length) return;
          let cursor = 0;
          matches.forEach(match => {
            const idx = match.index;
            if (idx > cursor) frag.appendChild(document.createTextNode(text.slice(cursor, idx)));
            const mark = document.createElement("mark");
            mark.className = "search-highlight";
            mark.textContent = match.value;
            frag.appendChild(mark);
            searchMatches.push(mark);
            cursor = idx + match.value.length;
          });
          if (cursor < text.length) frag.appendChild(document.createTextNode(text.slice(cursor)));
          textNode.parentNode.replaceChild(frag, textNode);
        });

        searchCount.textContent = searchMatches.length > 0 ? `${searchMatches.length}` : "0";
        if (searchMatches.length > 0) {
          activeMatchIndex = 0;
          focusMatch(0);
        }
        updateSearchNavButtons();
      }

      let searchDebounce;
      searchInput?.addEventListener("input", (e) => {
        clearTimeout(searchDebounce);
        searchDebounce = setTimeout(() => doSearch(e.target.value.trim()), 250);
      });
      searchInput?.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && searchMatches.length > 0) {
          e.preventDefault();
          activeMatchIndex = (activeMatchIndex + 1) % searchMatches.length;
          focusMatch(activeMatchIndex);
        }
        if (e.key === "Escape") {
          e.preventDefault();
          e.stopPropagation();
          if (searchInput.value) { searchInput.value = ""; clearSearch(); }
          else searchInput.blur();
        }
      });
      searchClearBtn?.addEventListener("click", () => { searchInput.value = ""; clearSearch(); searchInput.focus(); });
      searchPrevBtn?.addEventListener("click", () => {
        if (searchMatches.length === 0) return;
        activeMatchIndex = (activeMatchIndex - 1 + searchMatches.length) % searchMatches.length;
        focusMatch(activeMatchIndex);
      });
      searchNextBtn?.addEventListener("click", () => {
        if (searchMatches.length === 0) return;
        activeMatchIndex = (activeMatchIndex + 1) % searchMatches.length;
        focusMatch(activeMatchIndex);
      });

      // ============================================================
      // FLOATING NAV + SCROLL
      // ============================================================
      const floatingNav = document.getElementById("floating-nav");
      const scrollTopBtn = document.getElementById("scroll-top");
      const scrollBottomBtn = document.getElementById("scroll-bottom");

      chatContainer.addEventListener("scroll", () => {
        const scrollTop = chatContainer.scrollTop;
        const scrollHeight = chatContainer.scrollHeight;
        const clientHeight = chatContainer.clientHeight;
        const notAtTop = scrollTop > 200;
        const notAtBottom = scrollTop + clientHeight < scrollHeight - 200;
        const isSearching = document.body.classList.contains("searching");
        const shouldShow = (notAtTop || notAtBottom) && !isSearching;

        floatingNav.classList.toggle("visible", shouldShow);
        scrollTopBtn.style.display = notAtTop ? "flex" : "none";
        scrollBottomBtn.style.display = notAtBottom ? "flex" : "none";

        if (!chatContainer._scrollSaveRAF) {
          chatContainer._scrollSaveRAF = requestAnimationFrame(() => {
            try { localStorage.setItem(STORAGE_KEY_SCROLL, String(chatContainer.scrollTop)); } catch (e) {}
            chatContainer._scrollSaveRAF = null;
          });
        }
        updateActiveUserNav();
      }, { passive: true });

      scrollTopBtn?.addEventListener("click", () => chatContainer.scrollTo({ top: 0, behavior: "smooth" }));
      scrollBottomBtn?.addEventListener("click", () => chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: "smooth" }));

      // ============================================================
      // THEME TOGGLE
      // ============================================================
      const themeToggle = document.getElementById("theme-toggle");
      themeToggle?.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme");
        const next = current === "light" ? "dark" : "light";
        document.documentElement.setAttribute("data-theme", next);
        themeToggle.textContent = next === "light" ? "☀️" : "🌙";
        try { localStorage.setItem(STORAGE_KEY_THEME, next); } catch (e) {}
      });

      function slugForFile(text) { return String(text || "chat").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 50) || "chat"; }
      function decodeRaw(bubble) { const d=document.createElement("textarea"); d.innerHTML=bubble?.getAttribute("data-raw")||""; return d.value; }
      function exportChatMarkdown() {
        const title=document.getElementById("chat-title")?.textContent?.trim()||"Chat";
        let md=`# ${title}\n\n`;
        document.querySelectorAll(".message-row").forEach(row=>{ const role=row.dataset.role==="user"?"User":"AI"; const ts=row.querySelector(".meta-time")?.textContent?.trim()||""; md+=`## ${role}${ts?` (${ts})`:""}\n\n${decodeRaw(row.querySelector(".bubble"))}\n\n`; });
        const ts=new Date().toISOString().slice(0,19).replace(/[:T]/g,"-"); downloadAsFile(`${slugForFile(title)}-${ts}.md`,md); showToast("✓ Markdown diekspor");
      }
      function exportChatJSON() {
        const title=document.getElementById("chat-title")?.textContent?.trim()||"Chat";
        const created=document.getElementById("header-subtitle")?.textContent?.trim()||"";
        const messages=[...document.querySelectorAll(".message-row")].map(row=>({role:row.dataset.role==="user"?"user":"assistant",content:decodeRaw(row.querySelector(".bubble")),timestamp:row.querySelector(".meta-time")?.textContent?.trim()||""}));
        const json=JSON.stringify({title,created_at:created,messages},null,2); const blob=new Blob([json],{type:"application/json;charset=utf-8"}); const url=URL.createObjectURL(blob); const a=document.createElement("a"); const ts=new Date().toISOString().slice(0,19).replace(/[:T]/g,"-"); a.href=url;a.download=`${slugForFile(title)}-${ts}.json`;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);showToast("✓ JSON diekspor");
      }
      let roleFilter=localStorage.getItem("gw-role-filter")||"all";
      function setRoleFilter(role){ role=["all","user","ai"].includes(role)?role:"all"; roleFilter=role; localStorage.setItem("gw-role-filter",role); document.querySelectorAll(".message-row").forEach(row=>{const r=row.dataset.role==="user"?"user":"ai";row.style.display=role==="all"||r===role?"":"none";}); showToast(`Filter: ${role==="all"?"Semua":role==="user"?"User":"AI"}`); }
      function toggleAllCollapsible(){ const bubbles=[...document.querySelectorAll(".bubble.collapsible")]; const shouldExpand=bubbles.some(b=>!b.classList.contains("expanded")); bubbles.forEach(b=>{b.classList.toggle("expanded",shouldExpand); const t=b.parentElement?.querySelector(".collapse-toggle"); if(t){t.classList.toggle("expanded",shouldExpand);const l=t.querySelector(".label");if(l)l.textContent=shouldExpand?"Sembunyikan":"Tampilkan semua";}}); }

      // ============================================================
      // HEADER MENU
      // ============================================================
      const headerMenuDropdown = document.getElementById("header-menu-dropdown");

      document.querySelectorAll(".header-menu-item").forEach(item => {
        item.addEventListener("click", (e) => {
          e.stopPropagation();
          const action = item.getAttribute("data-action");
          if (action === "print") window.print();
          if (action === "export-md") exportChatMarkdown();
          if (action === "export-json") exportChatJSON();
          if (action?.startsWith("role-")) setRoleFilter(action.slice(5));
          if (action === "collapse-all") toggleAllCollapsible();
          closeHeaderMenuEarly();
        });
      });

      setRoleFilter(roleFilter);

      // ============================================================
      // HELP MODAL
      // ============================================================
      const helpOverlay = helpOverlayEarly;

      const openHelp = openHelpEarly;
      const closeHelp = closeHelpEarly;

      // ============================================================
      // KEYBOARD SHORTCUTS
      // ============================================================
      document.addEventListener("keydown", (e) => {
        const tag = (e.target.tagName || "").toLowerCase();
        if (tag === "input" || tag === "textarea") return;

        if (e.key === "?" && !e.ctrlKey && !e.metaKey) {
          e.preventDefault();
          if (helpOverlay?.classList.contains("visible")) closeHelp();
          else openHelp();
          return;
        }

        if (e.key === "Escape") {
          if (helpOverlay?.classList.contains("visible")) { closeHelp(); return; }
          if (document.body.classList.contains("searching")) {
            searchInput.value = "";
            clearSearch();
            searchInput.blur();
            return;
          }
          if (!sidebar.classList.contains("collapsed")) closeSidebar();
          if (!rightRail.classList.contains("collapsed")) closeRightRail();
          closeHeaderMenu();
          return;
        }

        if (e.key === "/") { e.preventDefault(); searchInput?.focus(); }
        else if (e.key === "j" || e.key === "k") {
          e.preventDefault();
          const rows = Array.from(document.querySelectorAll(".message-row"));
          const scrollTop = chatContainer.scrollTop;
          const viewportMid = scrollTop + chatContainer.clientHeight / 2;
          if (e.key === "j") {
            const next = rows.find(r => r.offsetTop > viewportMid + 50);
            if (next) next.scrollIntoView({ behavior: "smooth", block: "start" });
          } else {
            const prev = [...rows].reverse().find(r => r.offsetTop < viewportMid - 50);
            if (prev) prev.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        } else if (e.key === "Home" && !e.ctrlKey) {
          chatContainer.scrollTo({ top: 0, behavior: "smooth" });
        } else if (e.key === "End" && !e.ctrlKey) {
          chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: "smooth" });
        }
      });

      // ============================================================
      // VISUAL VIEWPORT (keyboard mobile)
      // ============================================================
      (function setupVisualViewport() {
        if (!window.visualViewport) return;
        const vv = window.visualViewport;
        const docEl = document.documentElement;
        function updateViewportHeight() {
          docEl.style.setProperty("--vv-height", vv.height + "px");
          const isKeyboardActive = vv.height < window.innerHeight - 100;
          document.body.classList.toggle("keyboard-active", isKeyboardActive);
        }
        updateViewportHeight();
        vv.addEventListener("resize", updateViewportHeight);
        vv.addEventListener("scroll", updateViewportHeight);
      })();

      // ============================================================
      // SWIPE GESTURES
      // ============================================================
      (function setupSwipeGestures() {
        const EDGE_ZONE = 50;
        const SWIPE_THRESHOLD = 50;
        const MAX_VERTICAL = 100;
        const MAX_DURATION = 800;
        let startX = 0, startY = 0, startTime = 0, startTarget = null, tracking = false, fromEdge = false;

        function isInteractive(el) {
          while (el && el !== document.body) {
            const tag = el.tagName?.toLowerCase();
            if (["input", "textarea", "button", "code", "pre", "a", "select", "video", "audio"].includes(tag)) return true;
            el = el.parentElement;
          }
          return false;
        }

        document.addEventListener("touchstart", (e) => {
          if (e.touches.length !== 1) { tracking = false; return; }
          const touch = e.touches[0];
          startX = touch.clientX;
          startY = touch.clientY;
          startTime = Date.now();
          startTarget = e.target;
          fromEdge = startX <= EDGE_ZONE || startX >= window.innerWidth - EDGE_ZONE;
          const inOpenSidebar = startTarget.closest && startTarget.closest(".sidebar:not(.collapsed)");
          const inOpenRail = startTarget.closest && startTarget.closest(".right-rail:not(.collapsed)");
          if (!fromEdge && !inOpenSidebar && !inOpenRail && isInteractive(startTarget)) {
            tracking = false;
            return;
          }
          tracking = true;
        }, { passive: true });

        document.addEventListener("touchend", (e) => {
          if (!tracking) return;
          if (e.changedTouches.length !== 1) { tracking = false; return; }
          tracking = false;
          const touch = e.changedTouches[0];
          const deltaX = touch.clientX - startX;
          const deltaY = Math.abs(touch.clientY - startY);
          const duration = Date.now() - startTime;
          if (duration > MAX_DURATION) return;
          if (deltaY > MAX_VERTICAL) return;
          if (Math.abs(deltaX) < SWIPE_THRESHOLD) return;
          const swipedRight = deltaX > 0;
          const swipedLeft = deltaX < 0;
          const sidebarEl = document.getElementById("sidebar");
          const rightRailEl = document.getElementById("right-rail");
          const sidebarOpen = sidebarEl && !sidebarEl.classList.contains("collapsed");
          const rightRailOpen = rightRailEl && !rightRailEl.classList.contains("collapsed");

          if (sidebarOpen && swipedLeft) { closeSidebar(); return; }
          if (rightRailOpen && swipedRight) { closeRightRail(); return; }
          if (!sidebarOpen && swipedRight) {
            if (fromEdge || startX < window.innerWidth / 2) {
              if (rightRailOpen) closeRightRail();
              openSidebar();
            }
            return;
          }
          if (!rightRailOpen && swipedLeft) {
            if (fromEdge || startX > window.innerWidth / 2) {
              if (sidebarOpen) closeSidebar();
              openRightRail();
            }
            return;
          }
        }, { passive: true });
      })();

      // ============================================================
      // ZOOM FIX
      // ============================================================
      (function setupZoomFix() {
        let lastDPR = window.devicePixelRatio;
        function checkZoom() {
          const currentDPR = window.devicePixelRatio;
          const zoomRatio = currentDPR / lastDPR;
          if (Math.abs(zoomRatio - 1) > 0.3) document.body.classList.add("zoomed");
          else document.body.classList.remove("zoomed");
          lastDPR = currentDPR;
        }
        window.addEventListener("resize", checkZoom);
        checkZoom();
      })();

      // ============================================================
      // RESTORE SCROLL
      // ============================================================
      (function restoreScroll() {
        try {
          const saved = localStorage.getItem(STORAGE_KEY_SCROLL);
          if (saved && parseInt(saved, 10) > 100) {
            requestAnimationFrame(() => { chatContainer.scrollTop = parseInt(saved, 10); });
          }
        } catch (e) {}
      })();

      // ============================================================
      // INITIAL LAYOUT
      // ============================================================
      if (window.innerWidth > 1024) openRightRail();
      else document.body.classList.add("right-rail-collapsed");

      // ============================================================
      // STEP 8 — REVEAL
      // ============================================================
      // Do NOT await requestAnimationFrame/timers here. On some mobile
      // WebViews a queued frame/timer can be suspended indefinitely,
      // leaving the loader permanently at 95%.
      //
      // All expensive work is already completed above. Mark the final
      // step synchronously and dismiss immediately; Progress.dismiss()
      // retains the minimum display time.
      Progress.setTask("reveal", true);
      await Progress.dismiss();
    });

    // ============================================================
    // UTILITY (global, dipanggil dari onclick di HTML)
    // ============================================================
    function copyCode(button) {
      const pre = button.closest("pre");
      const code = pre.querySelector("code").innerText;
      navigator.clipboard.writeText(code).then(() => {
        button.innerText = "Copied!";
        setTimeout(() => { button.innerText = "Copy"; }, 2000);
      }).catch(() => {
        button.innerText = "Gagal copy";
        setTimeout(() => { button.innerText = "Copy"; }, 2000);
      });
    }

    function escapeHtml(text) {
      const div = document.createElement("div");
      div.textContent = text;
      return div.innerHTML;
    }
