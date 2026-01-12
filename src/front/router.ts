export class Router {
  constructor(container, trackPlayer) {
    this.container = container;
    this.trackPlayer = trackPlayer;
    this.routes = {};
    window.addEventListener("popstate", () => this.onRouteChange());
    document.body.addEventListener("click", (e) => {
      const anchor = e.target.closest("a");
      if (anchor && anchor.hasAttribute("data-link")) {
        e.preventDefault();
        this.navigate(anchor.getAttribute("href"));
      }
    });
  }

  register(path, handler) {
    this.routes[path] = handler;
  }

  onRouteChange() {
    let path = window.location.pathname;
    if (path === "") path = "/";

    for (const route in this.routes) {
      const params = this.match(route, path);
      if (params) {
        this.routes[route](this.container, params, this.trackPlayer);
        return;
      }
    }
    // If no route is matched, you might want to render a 404 page
    // or redirect to a default page.
    if (this.routes["/"]) {
      this.routes["/"](this.container, {}, this.trackPlayer);
    }
  }

  match(route, path) {
    const routeParts = route.split("/").filter((p) => p);
    const pathParts = path.split("/").filter((p) => p);

    if (routeParts.length !== pathParts.length) {
      return null;
    }

    const params = {};
    for (let i = 0; i < routeParts.length; i++) {
      if (routeParts[i].startsWith(":")) {
        params[routeParts[i].slice(1)] = pathParts[i];
      } else if (routeParts[i] !== pathParts[i]) {
        return null;
      }
    }
    return params;
  }

  navigate(path) {
    window.history.pushState({}, "", path);
    this.onRouteChange();
  }
}
