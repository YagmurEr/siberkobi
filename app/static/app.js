document.addEventListener("DOMContentLoaded", () => {
  const printButton = document.querySelector('[data-action="print"]');
  if (printButton) {
    printButton.addEventListener("click", () => window.print());
  }

  const scanForm = document.querySelector("[data-scan-form]");
  const scanProgress = document.querySelector("[data-scan-progress]");
  if (scanForm && scanProgress) {
    scanForm.addEventListener("submit", (event) => {
      event.preventDefault();
      scanProgress.hidden = false;
      scanProgress.classList.add("is-running");
      scanProgress.scrollIntoView({ behavior: "smooth", block: "center" });

      const submitButton = scanForm.querySelector('button[type="submit"]');
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = "Analiz çalışıyor…";
      }

      const steps = [...scanProgress.querySelectorAll("[data-progress-step]")];
      steps.forEach((step) => step.classList.remove("is-active", "is-done"));
      let index = 0;
      if (steps.length) {
        steps[0].classList.add("is-active");
      }

      const timer = window.setInterval(() => {
        if (index < steps.length) {
          steps[index].classList.remove("is-active");
          steps[index].classList.add("is-done");
          index += 1;
        }
        if (index < steps.length) {
          steps[index].classList.add("is-active");
        } else {
          window.clearInterval(timer);
          index = Math.max(0, steps.length - 1);
          steps[index]?.classList.add("is-active");
        }
      }, 900);

      window.setTimeout(() => scanForm.submit(), 120);
    });
  }

  const assessmentForm = document.querySelector("[data-assessment-form]");
  const authorizationCheckbox = document.querySelector("[data-authorization-checkbox]");
  const submitButton = document.querySelector("[data-submit-button]");

  if (assessmentForm && authorizationCheckbox && submitButton) {
    const syncAuthorizationState = () => {
      submitButton.disabled = !authorizationCheckbox.checked;
    };

    authorizationCheckbox.addEventListener("change", syncAuthorizationState);
    syncAuthorizationState();
  }
});
