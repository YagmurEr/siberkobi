document.addEventListener("DOMContentLoaded", () => {
  const printButton = document.querySelector('[data-action="print"]');
  if (printButton) {
    printButton.addEventListener("click", () => window.print());
  }

  const scanForm = document.querySelector("[data-scan-form]");
  const scanProgress = document.querySelector("[data-scan-progress]");
  if (scanForm && scanProgress) {
    scanForm.addEventListener("submit", () => {
      scanProgress.hidden = false;
      scanProgress.scrollIntoView({ behavior: "smooth", block: "center" });
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
