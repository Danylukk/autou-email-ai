document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("email-form");
  const btnSubmit = document.getElementById("btn-submit");
  const btnDemo = document.getElementById("btn-demo");
  const btnCopy = document.getElementById("btn-copy");
  const metricProd = document.getElementById("metric-prod");
  const metricImprod = document.getElementById("metric-improd");

  if (form && btnSubmit) {
    form.addEventListener("submit", () => {
      document.body.classList.add("is-loading");
      btnSubmit.disabled = true;
    });
  }

  if (btnDemo) {
    btnDemo.addEventListener("click", () => {
      const textarea = document.getElementById("email_text");
      if (!textarea) return;

      const exemplos = [
        `Olá, tudo bem?

Estou acompanhando uma solicitação de reembolso aberta na semana passada
e ainda não recebi retorno. Poderiam, por favor, me informar o status
do processo e o prazo estimado para conclusão?

Obrigado desde já.`,
        `Oi, equipe!

Queria apenas agradecer pelo suporte de vocês esse ano. O atendimento
foi sempre muito rápido e atencioso. Aproveito para desejar um ótimo
fim de ano e muito sucesso!

Abraços.`
      ];

      const random = Math.random() < 0.5 ? 0 : 1;
      textarea.value = exemplos[random];
      textarea.focus();
    });
  }

  if (btnCopy) {
    btnCopy.addEventListener("click", () => {
      const output = document.querySelector(".output-text");
      if (!output) return;
      output.select();
      document.execCommand("copy");
      btnCopy.textContent = "Copiado!";
      setTimeout(() => {
        btnCopy.textContent = "Copiar resposta";
      }, 1800);
    });
  }

  // Anima de leve as métricas, só para dar vida à UI no vídeo
  if (metricProd && metricImprod) {
    let baseProd = parseInt(metricProd.textContent, 10) || 37;
    let baseImprod = parseInt(metricImprod.textContent, 10) || 19;

    setInterval(() => {
      const prodOffset = Math.floor(Math.random() * 4) - 2;
      const improdOffset = Math.floor(Math.random() * 4) - 2;
      metricProd.textContent = String(Math.max(0, baseProd + prodOffset));
      metricImprod.textContent = String(Math.max(0, baseImprod + improdOffset));
    }, 3500);
  }
});
