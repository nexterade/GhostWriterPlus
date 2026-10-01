from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / 'templates/viewer/script.js').read_text(encoding='utf-8')
CSS = (ROOT / 'templates/viewer/style.css').read_text(encoding='utf-8')


def test_code_controls_do_not_depend_on_highlightjs():
    assert 'if (typeof hljs !== "undefined") {' in JS
    assert 'code-copy-btn' in JS
    assert 'dataset.innerCollapse' in JS


def test_inner_code_collapse_has_real_css_target():
    assert '.markdown-body pre.code-collapsed > code' in CSS
    assert '.code-collapsed pre' not in CSS


def test_inner_collapse_is_nested_inside_message_bubble():
    assert 'pre.parentNode.insertBefore(wrap, pre)' in JS
    assert 'wrap.appendChild(pre)' in JS
    assert 'wrap.appendChild(all)' in JS


def test_code_copy_button_is_visible_and_bound():
    assert 'class="code-copy-btn"' in JS
    assert 'action==="copy"' in JS
    assert 'navigator.clipboard.writeText(getCodeText(pre))' in JS
