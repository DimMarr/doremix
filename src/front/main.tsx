import "@styles/alert.css";
import { HomePage, PlaylistDetailPage, LoginPage, SignupPage, AdminPage, ArtistsPage, ArtistTracksPage } from "@pages/index";
import { createMainLayout, trackPlayerInstance } from "@layouts/mainLayout";
import { Router } from "./router";
import { CguPage } from "./pages/cgu";
import { NoInternetPage } from "@pages/noInternet";
import { VerifyEmailPage } from "@pages/verifyEmail";

export let routerInstance = null;

export default async function init() {
  if(!navigator.onLine){
    document.getElementById("app").innerHTML = NoInternetPage() as unknown as string;
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

  router.register("/cgu", async(container) => {
    CguPage(container);
  })

  router.register("/artists", (container, params) => {
    ArtistsPage(container, (path) => router.navigate(path));
  });

  router.register("/artists/:id", async (container, params) => {
    ArtistTracksPage(container, () => router.navigate("/artists"), params);
  });

  router.register("/verify-email", async(container) => {
    VerifyEmailPage(container);
  })

  router.register("/cgu", async(container) => {
    CguPage(container);
  })

  router.onRouteChange();
  routerInstance = router;
}

init();
