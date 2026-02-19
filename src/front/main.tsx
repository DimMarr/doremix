import "@styles/alert.css";
import { HomePage, PlaylistDetailPage, LoginPage, SignupPage, AdminPage } from "@pages/index";
import { createMainLayout, trackPlayerInstance } from "@layouts/mainLayout";
import { Router } from "./router";
import { NoInternetPage } from "@pages/noInternet";

export let routerInstance = null;

export default async function init() {
  if(!navigator.onLine){
    document.getElementById("app").innerHTML = NoInternetPage();
    return;
  }

  const { mainContent } = await createMainLayout();
  const router = new Router(mainContent, trackPlayerInstance);

  router.register("/", (container, params) => {
    HomePage(container);
  });

  router.register("/playlist/:id", async (container, params) => {
    PlaylistDetailPage(container, () => router.navigate("/"), params);
  });

  router.register("/login", async(container, params) => {
    LoginPage(container);
  })

  router.register("/signup", async(container) => {
    SignupPage(container);
  })

  router.register("/admin", async(container) => {
    AdminPage(container);
  })

  router.onRouteChange();
  routerInstance = router;
}

init();
