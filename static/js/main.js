/**
 * NLP Toolkit Frontend Controller
 */

const API_ENDPOINTS = {
    paraphrase: '/paraphrase',
    humanize: '/humanize',
    grammar: '/grammar',
    summarize: '/summarize'
};

const TOOL_META = {
    paraphrase: {
        title: 'Text Paraphraser',
        desc: 'Generate multiple rephrased versions of your text while preserving meaning.',
        action: 'Paraphrase',
        placeholder: 'Enter text to paraphrase...'
    },
    humanize: {
        title: 'Text Humanizer',
        desc: 'Rewrite AI-generated text to sound more natural and human-like.',
        action: 'Humanize',
        placeholder: 'Paste AI-generated text here...'
    },
    grammar: {
        title: 'Grammar Correction',
        desc: 'Fix grammatical errors, spelling mistakes, and improve sentence structure.',
        action: 'Fix Grammar',
        placeholder: 'Enter text with grammar issues...'
    },
    summarize: {
        title: 'Text Summarizer',
        desc: 'Condense long articles, paragraphs, or documents into concise summaries.',
        action: 'Summarize',
        placeholder: 'Paste long text to summarize...'
    }
};

// ─── DOM Elements ──────────────────────────────────────────────────────────
const els = {
    navItems: document.querySelectorAll('.nav-item'),
    pageTitle: document.getElementById('page-title'),
    pageDesc: document.getElementById('page-desc'),
    inputText: document.getElementById('input-text'),
    inputCount: document.getElementById('input-count'),
    actionBtn: document.getElementById('action-btn'),
    btnText: document.querySelector('.btn-text'),
    btnSpinner: document.getElementById('btn-spinner'),
    clearBtn: document.getElementById('clear-btn'),
    outputBody: document.getElementById('output-body'),
    copyBtn: document.getElementById('copy-btn'),
    toast: document.getElementById('toast'),
    toastMsg: document.getElementById('toast-msg'),
    statusDot: document.getElementById('status-dot'),
    statusText: document.getElementById('status-text')
};

let currentTool = 'paraphrase';
let isLoading = false;

// ─── Initialization ────────────────────────────────────────────────────────
function init() {
    els.navItems.forEach(item => {
        item.addEventListener('click', () => switchTool(item.dataset.tool));
    });

    els.actionBtn.addEventListener('click', handleAction);
    els.clearBtn.addEventListener('click', clearAll);
    els.copyBtn.addEventListener('click', copyOutput);
    els.inputText.addEventListener('input', updateCharCount);

    // Keyboard shortcut: Ctrl+Enter to submit
    els.inputText.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            handleAction();
        }
    });

    updateCharCount();
}

// ─── Tool Switching ────────────────────────────────────────────────────────
function switchTool(tool) {
    if (isLoading) return;
    currentTool = tool;

    // Update nav
    els.navItems.forEach(item => {
        item.classList.toggle('active', item.dataset.tool === tool);
    });

    // Update header
    const meta = TOOL_META[tool];
    els.pageTitle.textContent = meta.title;
    els.pageDesc.textContent = meta.desc;
    els.btnText.textContent = meta.action;
    els.inputText.placeholder = meta.placeholder;

    // Clear output
    clearOutput();
}

// ─── Character Counter ─────────────────────────────────────────────────────
function updateCharCount() {
    const len = els.inputText.value.length;
    els.inputCount.textContent = `${len} char${len !== 1 ? 's' : ''}`;
}

// ─── Clear ─────────────────────────────────────────────────────────────────
function clearAll() {
    els.inputText.value = '';
    updateCharCount();
    clearOutput();
}

function clearOutput() {
    els.outputBody.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">📝</div>
            <p>Your results will appear here</p>
        </div>
    `;
}

// ─── Main Action ───────────────────────────────────────────────────────────
async function handleAction() {
    const text = els.inputText.value.trim();
    if (!text) {
        showToast('Please enter some text first', 'warning');
        return;
    }

    if (isLoading) return;

    setLoading(true);
    clearOutput();

    try {
        const response = await fetch(API_ENDPOINTS[currentTool], {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Something went wrong');
        }

        renderOutput(data);
    } catch (err) {
        els.outputBody.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">⚠️</div>
                <p style="color: var(--danger);">${escapeHtml(err.message)}</p>
            </div>
        `;
    } finally {
        setLoading(false);
    }
}

// ─── Render Output ─────────────────────────────────────────────────────────
function renderOutput(data) {
    if (currentTool === 'paraphrase' && data.results) {
        renderParaphraseResults(data.results);
    } else if (data.result) {
        renderSingleResult(data.result);
    } else {
        clearOutput();
    }
}

function renderParaphraseResults(results) {
    const container = document.createElement('div');
    container.style.paddingRight = '8px';

    results.forEach((text, idx) => {
        const card = document.createElement('div');
        card.className = 'result-card';
        card.dataset.index = idx + 1;
        card.textContent = text;
        card.title = 'Click to copy';
        card.addEventListener('click', () => {
            navigator.clipboard.writeText(text);
            showToast(`Variant ${idx + 1} copied!`);

            // Visual feedback
            document.querySelectorAll('.result-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
        });
        container.appendChild(card);
    });

    els.outputBody.innerHTML = '';
    els.outputBody.appendChild(container);
}

function renderSingleResult(text) {
    const div = document.createElement('div');
    div.className = 'result-text';
    div.textContent = text;
    els.outputBody.innerHTML = '';
    els.outputBody.appendChild(div);
}

// ─── Copy ──────────────────────────────────────────────────────────────────
async function copyOutput() {
    let text = '';

    if (currentTool === 'paraphrase') {
        const selected = document.querySelector('.result-card.selected');
        if (selected) {
            text = selected.textContent;
        } else {
            const first = document.querySelector('.result-card');
            if (first) text = first.textContent;
        }
    } else {
        const resultDiv = document.querySelector('.result-text');
        if (resultDiv) text = resultDiv.textContent;
    }

    if (!text) {
        showToast('Nothing to copy', 'warning');
        return;
    }

    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard!');
    } catch {
        showToast('Failed to copy', 'error');
    }
}

// ─── UI State ──────────────────────────────────────────────────────────────
function setLoading(loading) {
    isLoading = loading;
    els.actionBtn.disabled = loading;
    els.btnText.textContent = loading ? TOOL_META[currentTool].action + '...' : TOOL_META[currentTool].action;
    els.btnSpinner.classList.toggle('hidden', !loading);

    if (loading) {
        els.statusDot.classList.add('loading');
        els.statusText.textContent = 'Processing...';
    } else {
        els.statusDot.classList.remove('loading');
        els.statusText.textContent = 'Ready';
    }
}

function showToast(msg, type = 'success') {
    els.toastMsg.textContent = msg;
    els.toast.classList.add('show');

    if (type === 'error') {
        els.toast.style.borderColor = 'var(--danger)';
    } else if (type === 'warning') {
        els.toast.style.borderColor = 'var(--warning)';
    } else {
        els.toast.style.borderColor = 'var(--border)';
    }

    setTimeout(() => {
        els.toast.classList.remove('show');
    }, 2500);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ─── Boot ──────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', init);
