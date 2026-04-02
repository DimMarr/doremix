import "@styles/alert.css";
import { HomePage, PlaylistDetailPage, LoginPage, SignupPage, AdminPage, VerifyEmailPage, ArtistsPage, ArtistTracksPage } from "@pages/index";
import { createMainLayout, trackPlayerInstance } from "@layouts/mainLayout";
import { Router } from "./router";
import { CguPage } from "./pages/cgu";
import { NoInternetPage } from "@pages/noInternet";
import { RequestPasswordResetPage } from "./pages/requestPasswordReset";
import { ResetPasswordPage } from "./pages/resetPassword";

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

  router.register("/artists", async (container) => {
    ArtistsPage(container, (path) => router.navigate(path));
  });

  router.register("/artists/:id", async (container, params) => {
    ArtistTracksPage(container, () => router.navigate("/artists"), params);
  });

  router.register("/verify-email", async(container) => {
    VerifyEmailPage(container);
  })

  router.register("/reset-password", async(container, params) => {
    ResetPasswordPage(container, params);
  })

  router.register("/request-password-reset", async(container) => {
    RequestPasswordResetPage(container);
  })

  router.register("/cgu", async(container) => {
    CguPage(container);
  })

  router.onRouteChange();
  routerInstance = router;
}

init();
