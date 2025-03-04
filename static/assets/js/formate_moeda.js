document.addEventListener("DOMContentLoaded", function () {
    const inputValor = document.querySelector("#valor_venda");

    if (inputValor) {
        inputValor.addEventListener("input", function (e) {
            let value = e.target.value.replace(/\D/g, ""); // Remove tudo que não for número
            let formattedValue = new Intl.NumberFormat("pt-BR", {
                style: "currency",
                currency: "BRL",
                minimumFractionDigits: 2,
            }).format(parseFloat(value) / 100);

            e.target.value = formattedValue;
        });

        inputValor.addEventListener("blur", function (e) {
            if (!e.target.value) {
                e.target.value = "0,00";
            }
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const element = document.querySelector('#valor_venda_formatado');
    
    if (element) {
        let value = element.innerText.replace('R$', '').trim(); // Remove o 'R$' e os espaços
        let formattedValue = parseFloat(value).toLocaleString('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        });
        element.innerText = formattedValue; // Atualiza o texto com o valor formatado
    }
});