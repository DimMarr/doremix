import { Sanitize } from '@utils/sanitize';
import { NoInternetPage } from "@pages/noInternet";
import { authService } from '@utils/authentication';

export enum AppRoutes {
  VERIFY_EMAIL = '/verify-email',
  LOGIN = '/login',
  SIGNUP = '/signup',
  HOME = '/',
}

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
        const href = anchor.getAttribute("href");
        if (href && (new Sanitize()).isValidPath(href)) {
          this.navigate(href);
        }
      }
    });
  }

  register(path, handler) {
    this.routes[path] = handler;
  }

  async onRouteChange() {
    if (navigator.onLine === false) {
      this.container.innerHTML = NoInternetPage();
      return;
    }

    // Gestion de l'authentification
    let path = window.location.pathname;
    const publicRoutes = [AppRoutes.LOGIN, AppRoutes.SIGNUP, AppRoutes.VERIFY_EMAIL];
    let isAuth = false;
    try {
      isAuth = await authService.isAuthenticated();
    } catch (e) {
      console.error("Auth check failed, assuming not authenticated:", e);
      isAuth = false;
    }

    if (!publicRoutes.includes(path as AppRoutes) && !isAuth) {
      window.history.pushState({}, "", AppRoutes.LOGIN);
      if (this.routes[AppRoutes.LOGIN]) {
        this.routes[AppRoutes.LOGIN](this.container, {}, {});
      }
      return;
    }

    if (publicRoutes.includes(path as AppRoutes) && isAuth) {
      window.history.pushState({}, "", AppRoutes.HOME);
      if (this.routes[AppRoutes.HOME]) {
        this.routes[AppRoutes.HOME](this.container, {}, {});
      }
      return;
    }

    if (path === "") path = AppRoutes.HOME;

    if (!(new Sanitize()).isValidPath(path)) {
      console.warn('Invalid path detected:', path);
      if (this.routes[AppRoutes.HOME]) {
        this.routes[AppRoutes.HOME](this.container, {}, this.trackPlayer);
      }
      return;
    }

    for (const route in this.routes) {
      const params = this.match(route, path);
      if (params) {
        this.routes[route](this.container, params, this.trackPlayer);
        return;
      }
    }
    // If no route is matched, you might want to render a 404 page
    // or redirect to a default page.
    if (this.routes[AppRoutes.HOME]) {
      this.routes[AppRoutes.HOME](this.container, {}, this.trackPlayer);
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
        params[routeParts[i].slice(1)] = decodeURIComponent(pathParts[i]);
      } else if (routeParts[i] !== pathParts[i]) {
        return null;
      }
    }

    return (new Sanitize()).sanitizeParams(params);
  }

  async navigate(path) {
    if (!(new Sanitize()).isValidPath(path)) {
      console.warn('Invalid navigation path:', path);
      return;
    }

    const sanitizedPath = (new Sanitize()).sanitizePath(path);

    if (!(new Sanitize()).isValidPath(sanitizedPath)) {
      console.warn('Sanitized path is invalid:', sanitizedPath);
      return;
    }

    window.history.pushState({}, "", sanitizedPath);
    await this.onRouteChange();
  }
}
