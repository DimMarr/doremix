export class AlertManager {
  private container: HTMLElement;
  private timeout: number;

  constructor(timeout = 100000) {
    this.timeout = timeout;
    this.container = this.createContainer();
  }

  private createContainer(): HTMLElement {
    let container = document.getElementById("alert-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "alert-container";
      document.body.appendChild(container);
    }
    return container;
  }

  private show(message: string, type: "success" | "warning" | "error") {
    const alert = document.createElement("div");
    alert.className = `alert ${type}`;
    alert.textContent = message;

    this.container.appendChild(alert);

    requestAnimationFrame(() => {
      alert.classList.add("show");
    });

    setTimeout(() => {
      alert.classList.remove("show");
      setTimeout(() => alert.remove(), 200);
    }, this.timeout);
  }

  success(message: string) {
    this.show(message, "success");
  }

  warning(message: string) {
    this.show(message, "warning");
  }

  error(message: string) {
    this.show(message, "error");
  }
}
