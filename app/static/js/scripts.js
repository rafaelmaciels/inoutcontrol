// ============================================================
// MODO ESCURO (Dark Mode) com localStorage
// ============================================================

// Obtém o toggle do modo escuro
const toggle = document.getElementById('darkModeToggle');

// Lê o modo salvo no navegador (default = light)
const currentMode = localStorage.getItem('darkMode') || 'light';

// Se o modo salvo for dark, aplica no body
if (currentMode === 'dark') {
    document.body.classList.add('dark-mode');
    if (toggle) toggle.checked = true; // marca o checkbox
}

// Listener para alternar entre claro/escuro
if (toggle) {
    toggle.addEventListener('change', function () {
        if (this.checked) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('darkMode', 'dark');
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('darkMode', 'light');
        }
        // Atualiza imediatamente o gráfico do Dashboard com o novo tema
        renderTopPecasChart();
    });
}



// ============================================================
// MODAL DE DEVOLUÇÃO — Preenche ID e abre modal
// ============================================================

function abrirModalDevolver(id) {
    const hiddenId = document.getElementById('mov_id');
    const form = document.getElementById('formDevolver');
    const modalEl = document.getElementById('modalDevolver');

    // Só executa se todos os elementos existirem
    if (hiddenId && form && modalEl) {
        hiddenId.value = id; // coloca o ID no campo hidden
        form.action = "/movimentacoes/devolver/" + id; // define a rota
        const modal = new bootstrap.Modal(modalEl);
        modal.show(); // abre o modal
    }
}



// ============================================================
// FECHAR MENSAGENS FLASH AUTOMATICAMENTE
// ============================================================

// Fecha alertas após 2 segundos
setTimeout(() => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}, 2000);



// ============================================================
// DASHBOARD — Gráfico de peças mais movimentadas
// ============================================================

function renderTopPecasChart() {
    const canvas = document.getElementById('chartTopPecas');
    if (!canvas || typeof Chart === 'undefined') return;

    const rawLabels = canvas.getAttribute('data-labels');
    const rawValues = canvas.getAttribute('data-values');
    if (!rawLabels || !rawValues) return;

    let labels = [];
    let values = [];
    try {
        labels = JSON.parse(rawLabels);
        values = JSON.parse(rawValues);
    } catch (e) {
        return;
    }

    if (window.topPecasChartInstance) {
        window.topPecasChartInstance.destroy();
    }

    const isDark = document.body.classList.contains('dark-mode');
    const barBg = isDark ? '#38bdf8' : 'rgba(71, 85, 105, 0.85)';
    const barHover = isDark ? '#f97316' : '#1e293b';
    const axisColor = isDark ? '#94a3b8' : '#475569';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.05)';
    const tooltipBg = isDark ? '#070e1e' : '#1e293b';

    const ctx = canvas.getContext('2d');
    window.topPecasChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Movimentações',
                data: values,
                backgroundColor: barBg,
                hoverBackgroundColor: barHover,
                borderColor: isDark ? '#0284c7' : '#334155',
                borderWidth: 1,
                borderRadius: 4,
                maxBarThickness: 45
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 350
            },
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: tooltipBg,
                    borderColor: isDark ? '#38bdf8' : '#475569',
                    borderWidth: 1,
                    padding: 10,
                    titleFont: { size: 13, weight: '600' },
                    bodyFont: { size: 12 },
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return ` Quantidade: ${context.parsed.y} un. movimentadas`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0,
                        color: axisColor,
                        font: { size: 11 }
                    },
                    grid: {
                        color: gridColor
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: axisColor,
                        font: { size: 11 },
                        maxRotation: 20,
                        minRotation: 0,
                        autoSkip: true
                    }
                }
            }
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    renderTopPecasChart();
});



// ============================================================
// MÁSCARA DE TELEFONE — Formato (99) 99999-9999
// ============================================================

document.addEventListener("DOMContentLoaded", function () {
    const tel = document.getElementById("telefone");
    if (!tel) return; // evita erro se o campo não existir

    tel.addEventListener("input", function () {

        // Remove tudo que não for número
        let v = tel.value.replace(/\D/g, "");

        // Limita a 11 dígitos (DDD + número)
        if (v.length > 11) v = v.slice(0, 11);

        // Telefone fixo (10 dígitos)
        if (v.length <= 10) {
            tel.value = v
                .replace(/^(\d{2})(\d)/, "($1) $2") // (99) 3...
                .replace(/(\d{4})(\d)/, "$1-$2");   // (99) 3456-7890
        } 
        
        // Celular (11 dígitos)
        else {
            tel.value = v
                .replace(/^(\d{2})(\d)/, "($1) $2") // (99) 9...
                .replace(/(\d{5})(\d)/, "$1-$2");   // (99) 99987-7845
        }
    });
});



// ============================================================
// EDITOR DE TEXTO WYSIWYG (Quill) PARA TODOS OS TEXTAREAS
// ============================================================

function initWysiwygEditors() {
    if (typeof Quill === 'undefined') return;

    // Seleciona todos os textareas do sistema
    const textareas = document.querySelectorAll('textarea');
    
    textareas.forEach(textarea => {
        // Evita duplicar inicialização
        if (textarea.dataset.wysiwygInitialized === 'true') return;
        textarea.dataset.wysiwygInitialized = 'true';

        // Oculta visualmente o textarea original, preservando-o para a submissão do formulário
        textarea.style.display = 'none';

        // Container externo
        const wrapper = document.createElement('div');
        wrapper.className = 'wysiwyg-wrapper mb-3';

        // Container do editor Quill
        const editorContainer = document.createElement('div');
        editorContainer.className = 'wysiwyg-editor';
        
        // Define altura baseada no número de linhas (rows) original ou padrão
        const rows = parseInt(textarea.getAttribute('rows')) || 4;
        editorContainer.style.minHeight = `${Math.max(rows * 32, 110)}px`;

        // Insere o wrapper no lugar do textarea
        textarea.parentNode.insertBefore(wrapper, textarea.nextSibling);
        wrapper.appendChild(editorContainer);

        // Inicializa o Quill com toolbar completa
        const quill = new Quill(editorContainer, {
            theme: 'snow',
            placeholder: textarea.getAttribute('placeholder') || 'Digite aqui...',
            modules: {
                toolbar: [
                    [{ 'header': [1, 2, 3, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    [{ 'color': [] }, { 'background': [] }],
                    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                    [{ 'align': [] }],
                    ['link', 'clean']
                ]
            }
        });

        // Carrega conteúdo inicial se houver
        const initialValue = textarea.value;
        if (initialValue && initialValue.trim() !== '') {
            // Se o conteúdo inicial já tiver tags HTML, injeta como HTML, senão converte quebras de linha
            if (/<[a-z][\s\S]*>/i.test(initialValue)) {
                quill.root.innerHTML = initialValue;
            } else {
                quill.setText(initialValue);
            }
        }

        // Função de sincronização com o textarea
        const syncContent = () => {
            const html = quill.root.innerHTML;
            const text = quill.getText().trim();
            if (html === '<p><br></p>' || text.length === 0) {
                textarea.value = '';
            } else {
                textarea.value = html;
            }
        };

        // Sincroniza em tempo real a cada digitação
        quill.on('text-change', syncContent);

        // Garante sincronização no submit do formulário
        const form = textarea.closest('form');
        if (form) {
            form.addEventListener('submit', syncContent);
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    initWysiwygEditors();
});

// Suporte para modais Bootstrap (ex: devolução de empréstimo)
document.addEventListener("shown.bs.modal", () => {
    initWysiwygEditors();
});

