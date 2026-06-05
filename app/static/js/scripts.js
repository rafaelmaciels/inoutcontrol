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

document.addEventListener("DOMContentLoaded", () => {

    // Verifica se o backend enviou dados para o gráfico
    if (window.dashboardData) {
        const { labels, values } = window.dashboardData;
        const ctx = document.getElementById('chartTopPecas');

        // Só cria o gráfico se houver dados e o canvas existir
        if (ctx && labels.length > 0) {
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Quantidade movimentada',
                        data: values,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    plugins: {
                        legend: { display: false } // remove legenda
                    },
                    scales: {
                        y: { beginAtZero: true } // eixo Y começa no zero
                    }
                }
            });
        }
    }
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
// (RESERVADO) — Caso queira adicionar mais scripts do dashboard
// ============================================================

// Você pode adicionar novos gráficos aqui futuramente.
// Mantive o bloco para organização do arquivo.
