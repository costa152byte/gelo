// static/js/artgelo.js

document.addEventListener('DOMContentLoaded', function() {
    
    // ========== EFEITO DE FUNDO 3D ==========
    document.addEventListener('mousemove', function(e) {
        const heroTitle = document.querySelector('.hero-title h1');
        if (heroTitle) {
            const xAxis = (window.innerWidth / 2 - e.pageX) / 50;
            const yAxis = (window.innerHeight / 2 - e.pageY) / 50;
            heroTitle.style.transform = `perspective(800px) rotateX(${yAxis}deg) rotateY(${xAxis}deg)`;
        }
    });

    // ========== ANIMAÇÃO DE FLOCOS DE NEVE ==========
    function createSnowflakes() {
        const container = document.querySelector('.snowflakes');
        if (!container) return;
        
        const symbols = ['❄', '❅', '❆', '✦'];
        for (let i = 0; i < 30; i++) {
            const flake = document.createElement('div');
            flake.className = 'snowflake';
            flake.textContent = symbols[Math.floor(Math.random() * symbols.length)];
            flake.style.left = Math.random() * 100 + '%';
            flake.style.fontSize = Math.random() * 1.5 + 0.5 + 'em';
            flake.style.animationDuration = Math.random() * 15 + 8 + 's';
            flake.style.opacity = Math.random() * 0.5 + 0.2;
            container.appendChild(flake);
        }
    }
    createSnowflakes();

    // ========== VALIDAÇÃO DE FORMULÁRIOS EM TEMPO REAL ==========
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required], select[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
    });

    function validateField(field) {
        const parent = field.closest('.mb-3');
        const error = parent ? parent.querySelector('.text-danger') : null;
        
        if (field.validity.valid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            if (error) error.style.display = 'none';
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            if (error) error.style.display = 'block';
        }
    }

    // ========== MÁSCARAS DE INPUT ==========
    // Máscara para telefone
    const telefoneInputs = document.querySelectorAll('input[type="tel"], input[name*="telefone"]');
    telefoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = this.value.replace(/\D/g, '');
            if (value.length > 11) value = value.slice(0, 11);
            
            if (value.length > 2) {
                value = '(' + value.slice(0, 2) + ') ' + value.slice(2);
            }
            if (value.length > 10) {
                value = value.slice(0, 10) + '-' + value.slice(10);
            }
            this.value = value;
        });
    });

    // Máscara para CEP
    const cepInputs = document.querySelectorAll('input[name*="cep"]');
    cepInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = this.value.replace(/\D/g, '');
            if (value.length > 8) value = value.slice(0, 8);
            if (value.length > 5) {
                value = value.slice(0, 5) + '-' + value.slice(5);
            }
            this.value = value;
        });
    });

    // ========== BUSCA DE ENDEREÇO POR CEP ==========
    const cepInput = document.querySelector('input[name="cep"]');
    if (cepInput) {
        cepInput.addEventListener('blur', function() {
            const cep = this.value.replace(/\D/g, '');
            if (cep.length === 8) {
                fetch(`https://viacep.com.br/ws/${cep}/json/`)
                    .then(response => response.json())
                    .then(data => {
                        if (!data.erro) {
                            const ruaInput = document.querySelector('input[name="rua"]');
                            const bairroInput = document.querySelector('input[name="bairro"]');
                            const cidadeInput = document.querySelector('input[name="cidade"]');
                            
                            if (ruaInput) ruaInput.value = data.logradouro;
                            if (bairroInput) bairroInput.value = data.bairro;
                            if (cidadeInput) cidadeInput.value = data.localidade;
                            
                            // Disparar evento para atualizar campo de cidade
                            if (cidadeInput) {
                                cidadeInput.dispatchEvent(new Event('change'));
                            }
                        }
                    })
                    .catch(error => console.error('Erro ao buscar CEP:', error));
            }
        });
    }

    // ========== CARREGAMENTO DINÂMICO DE ENDEREÇOS ==========
    const clienteSelect = document.querySelector('#id_cliente');
    const enderecoSelect = document.querySelector('#id_endereco_entrega');

    if (clienteSelect && enderecoSelect) {
        clienteSelect.addEventListener('change', function() {
            const clienteId = this.value;
            if (!clienteId) {
                enderecoSelect.innerHTML = '<option value="">Selecione um cliente primeiro</option>';
                return;
            }

            // Buscar endereços do cliente via AJAX
            fetch(`/api/enderecos-por-membro/?membro_id=${clienteId}`)
                .then(response => response.json())
                .then(data => {
                    enderecoSelect.innerHTML = '';
                    if (data.results && data.results.length > 0) {
                        data.results.forEach(endereco => {
                            const option = document.createElement('option');
                            option.value = endereco.id;
                            option.textContent = endereco.text;
                            if (endereco.principal) {
                                option.textContent += ' (Principal)';
                            }
                            enderecoSelect.appendChild(option);
                        });
                    } else {
                        const option = document.createElement('option');
                        option.value = '';
                        option.textContent = 'Nenhum endereço cadastrado';
                        enderecoSelect.appendChild(option);
                    }
                })
                .catch(error => console.error('Erro ao carregar endereços:', error));
        });
    }

    // ========== CÁLCULO DE VALOR DO PEDIDO EM TEMPO REAL ==========
    let valorTimeout;

    function calcularValorPedido() {
        const itens = [];
        document.querySelectorAll('.item-pedido').forEach(row => {
            const produtoId = row.querySelector('[name*="produto"]')?.value;
            const quantidade = parseFloat(row.querySelector('[name*="quantidade"]')?.value);
            if (produtoId && quantidade > 0) {
                itens.push({ produto_id: produtoId, quantidade: quantidade });
            }
        });

        if (itens.length === 0) {
            document.querySelector('#valor-total-display').textContent = 'R$ 0,00';
            return;
        }

        fetch('/api/calcular-valor-pedido/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ itens: itens })
        })
        .then(response => response.json())
        .then(data => {
            document.querySelector('#valor-total-display').textContent = data.total_formatado;
        })
        .catch(error => console.error('Erro ao calcular valor:', error));
    }

    // Debounce para evitar chamadas excessivas
    document.addEventListener('input', function(e) {
        if (e.target.closest('.item-pedido')) {
            clearTimeout(valorTimeout);
            valorTimeout = setTimeout(calcularValorPedido, 500);
        }
    });

    // ========== FUNÇÃO PARA OBTER CSRF TOKEN ==========
    function getCSRFToken() {
        const cookieValue = document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)');
        return cookieValue ? cookieValue.pop() : '';
    }

    // ========== MENU INTERATIVO ==========
    const menuItems = document.querySelectorAll('.navbar-nav .nav-link');
    menuItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // ========== INTEGRAÇÃO COM WHATSAPP ==========
    const whatsappButtons = document.querySelectorAll('.btn-whatsapp');
    whatsappButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const mensagem = this.dataset.mensagem || 'Olá, estou interessado nos serviços da Artgelo!';
            const numero = this.dataset.numero || '5511999999999';
            const url = `https://wa.me/${numero}?text=${encodeURIComponent(mensagem)}`;
            window.open(url, '_blank');
        });
    });

    // ========== RESPONSIVIDADE ADICIONAL ==========
    function ajustarLayout() {
        const heroTitle = document.querySelector('.hero-title h1');
        if (heroTitle) {
            if (window.innerWidth < 768) {
                heroTitle.style.fontSize = '2.5rem';
            } else if (window.innerWidth < 992) {
                heroTitle.style.fontSize = '4rem';
            } else {
                heroTitle.style.fontSize = '6rem';
            }
        }
    }

    window.addEventListener('resize', ajustarLayout);
    ajustarLayout();
});