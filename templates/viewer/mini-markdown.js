/* GhostReader+ local rich-text fallback.
 * No CDN/network dependency. Defines the small `marked.parse()` surface used
 * by viewer/script.js, while preserving sanitized generated HTML blocks such
 * as attachment cards.
 */
(function () {
  "use strict";
  if (window.marked && typeof window.marked.parse === "function") return;

  const ALLOWED_TAGS = new Set([
    "a","abbr","b","blockquote","br","code","del","details","div","em","figcaption",
    "figure","h1","h2","h3","h4","h5","h6","hr","i","img","li","ol","p","pre",
    "small","span","strong","summary","table","tbody","td","tfoot","th","thead",
    "tr","u","ul"
  ]);
  const ALLOWED_ATTRS = new Set([
    "class","title","alt","href","src","target","rel","colspan","rowspan",
    "width","height","open","aria-label"
  ]);

  function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, c => ({
      "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
    }[c]));
  }

  function sanitizeFragment(html) {
    const parser = new DOMParser();
    const doc = parser.parseFromString("<!doctype html><body>" + html, "text/html");
    const root = doc.body;

    function clean(node) {
      for (const child of Array.from(node.childNodes)) {
        if (child.nodeType === Node.COMMENT_NODE) { child.remove(); continue; }
        if (child.nodeType !== Node.ELEMENT_NODE) continue;
        const tag = child.tagName.toLowerCase();
        if (!ALLOWED_TAGS.has(tag)) {
          child.replaceWith(...Array.from(child.childNodes));
          continue;
        }
        for (const attr of Array.from(child.attributes)) {
          const name = attr.name.toLowerCase();
          if (!ALLOWED_ATTRS.has(name) ||
              name.startsWith("on") ||
              (name === "href" && !/^(https?:|mailto:|#)/i.test(attr.value.trim())) ||
              (name === "src" && !/^(https?:|data:image\/(?:png|jpe?g|gif|webp);)/i.test(attr.value.trim()))) {
            child.removeAttribute(attr.name);
          }
        }
        if (tag === "a") {
          child.setAttribute("target", "_blank");
          child.setAttribute("rel", "noopener noreferrer");
        }
        clean(child);
      }
    }
    clean(root);
    return root.innerHTML;
  }

  // Protect generated HTML blocks before Markdown escaping. This is a small
  // balanced-tag scanner rather than a regex, so nested attachment <div>s work.
  function protectBlocks(raw) {
    const blocks = [];
    let text = String(raw ?? "");
    const openRe = /<(div|details|table|figure)\b[^>]*>/ig;

    function findEnd(start, tag) {
      const tokenRe = new RegExp("</?" + tag + "\\b[^>]*>", "ig");
      tokenRe.lastIndex = start;
      let depth = 1, m;
      while ((m = tokenRe.exec(text))) {
        const tok = m[0];
        if (/^<\//.test(tok)) depth--;
        else if (!/\/>$/.test(tok)) depth++;
        if (depth === 0) return m.index + tok.length;
      }
      return -1;
    }

    let out = "", cursor = 0, m;
    while ((m = openRe.exec(text))) {
      const tag = m[1].toLowerCase();
      const cls = m[0];
      // Only preserve HTML that is deliberately structural/generated. Generic
      // prose containing <div> is left to Markdown escaping.
      if (tag !== "div" && tag !== "details" && tag !== "table" && tag !== "figure") continue;
      if (tag === "div" && !/attachment-box|attachment-preview|attachment-info|attachment-text/i.test(cls)) continue;
      const end = findEnd(m.index + m[0].length, tag);
      if (end < 0) continue;
      out += text.slice(cursor, m.index);
      const key = `\u0000GWHTML${blocks.length}\u0000`;
      blocks.push(text.slice(m.index, end));
      out += key;
      cursor = end;
      openRe.lastIndex = end;
    }
    out += text.slice(cursor);
    return { text: out, blocks };
  }

  function inline(s) {
    let x = escapeHtml(s);
    x = x.replace(/`([^`\n]+)`/g, "<code>$1</code>");
    x = x.replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>");
    x = x.replace(/__([^_\n]+)__/g, "<strong>$1</strong>");
    x = x.replace(/~~([^~\n]+)~~/g, "<del>$1</del>");
    x = x.replace(/(^|[^\*])\*([^*\n]+)\*/g, "$1<em>$2</em>");
    x = x.replace(/(^|[^_])_([^_\n]+)_/g, "$1<em>$2</em>");
    x = x.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+|mailto:[^\s)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    x = x.replace(/  \n/g, "<br>");
    return x;
  }

  function restoreBlocks(html, blocks) {
    return html.replace(/\u0000GWHTML(\d+)\u0000/g, (_, i) => sanitizeFragment(blocks[Number(i)] || ""));
  }

  function parseTable(lines, start) {
    if (start + 1 >= lines.length) return null;
    const isSep = s => /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(s);
    if (!lines[start].includes("|") || !isSep(lines[start + 1])) return null;
    const cells = line => line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map(x => x.trim());
    const head = cells(lines[start]);
    let i = start + 2, body = "";
    while (i < lines.length && lines[i].trim() && lines[i].includes("|")) {
      body += "<tr>" + cells(lines[i]).map(c => `<td>${inline(c)}</td>`).join("") + "</tr>";
      i++;
    }
    return {
      html: `<table><thead><tr>${head.map(c => `<th>${inline(c)}</th>`).join("")}</tr></thead><tbody>${body}</tbody></table>`,
      next: i
    };
  }

  function parseMarkdown(source) {
    const protectedData = protectBlocks(source);
    const lines = protectedData.text.replace(/\r\n?/g, "\n").split("\n");
    const out = [];
    let i = 0;

    while (i < lines.length) {
      const line = lines[i];

      if (!line.trim()) { i++; continue; }

      // fenced code
      const fence = line.match(/^ {0,3}(```+|~~~+)\s*([\w.+-]*)\s*$/);
      if (fence) {
        const mark = fence[1][0], lang = fence[2] || "";
        i++;
        const code = [];
        while (i < lines.length && !new RegExp("^ {0,3}" + "\\" + mark + "{3,}\\s*$").test(lines[i])) {
          code.push(lines[i]); i++;
        }
        if (i < lines.length) i++;
        out.push(`<pre><code${lang ? ` class="language-${escapeHtml(lang)}"` : ""}>${escapeHtml(code.join("\n"))}</code></pre>`);
        continue;
      }

      const heading = line.match(/^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$/);
      if (heading) {
        const n = heading[1].length;
        out.push(`<h${n}>${inline(heading[2])}</h${n}>`); i++; continue;
      }

      if (/^ {0,3}(---+|\*\*\*+|___+)\s*$/.test(line)) {
        out.push("<hr>"); i++; continue;
      }

      const quote = [];
      while (i < lines.length && /^ {0,3}>\s?/.test(lines[i])) {
        quote.push(lines[i].replace(/^ {0,3}>\s?/, "")); i++;
      }
      if (quote.length) {
        out.push(`<blockquote>${parseMarkdown(quote.join("\n"))}</blockquote>`); continue;
      }

      const table = parseTable(lines, i);
      if (table) { out.push(table.html); i = table.next; continue; }

      if (/^\s*[-*+]\s+/.test(line)) {
        const items = [];
        while (i < lines.length && /^\s*[-*+]\s+/.test(lines[i])) {
          items.push(`<li>${inline(lines[i].replace(/^\s*[-*+]\s+/, ""))}</li>`); i++;
        }
        out.push(`<ul>${items.join("")}</ul>`); continue;
      }

      if (/^\s*\d+[.)]\s+/.test(line)) {
        const items = [];
        while (i < lines.length && /^\s*\d+[.)]\s+/.test(lines[i])) {
          items.push(`<li>${inline(lines[i].replace(/^\s*\d+[.)]\s+/, ""))}</li>`); i++;
        }
        out.push(`<ol>${items.join("")}</ol>`); continue;
      }

      // Structural protected HTML block.
      if (/^\u0000GWHTML\d+\u0000$/.test(line.trim())) {
        out.push(line.trim()); i++; continue;
      }

      const para = [line];
      i++;
      while (i < lines.length && lines[i].trim()) {
        if (/^ {0,3}(#{1,6})\s+/.test(lines[i]) ||
            /^ {0,3}>\s?/.test(lines[i]) ||
            /^\s*[-*+]\s+/.test(lines[i]) ||
            /^\s*\d+[.)]\s+/.test(lines[i]) ||
            /^ {0,3}(```+|~~~+)/.test(lines[i]) ||
            /^\u0000GWHTML\d+\u0000$/.test(lines[i].trim())) break;
        para.push(lines[i]); i++;
      }
      out.push(`<p>${inline(para.join("\n"))}</p>`);
    }
    return restoreBlocks(out.join(""), protectedData.blocks);
  }

  window.marked = { parse: parseMarkdown, use: function () {} };
})();
