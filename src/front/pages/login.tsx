import { Button, Input, Testimony } from "@components/generics";
import { AlertManager } from "@utils/alertManager";
import { isValidEmail, isValidPassword } from "@utils/authentication";
import { Card } from "@components/generics/card";
import { authService } from "@utils/authentication";

export async function LoginPage(container) {

    const pageHtml = (
        <div>
            {
                <div class="flex justify-center items-center h-[calc(100vh-64px)]">
                    <div class="flex flex-col lg:flex-row items-stretch" >
                        <div class="bg-(--color-secondary) rounded-t-lg lg:rounded-l-lg lg:rounded-tr-none p-10 flex flex-col justify-between gap-10" style="max-width: 600px;">
                            <div class="flex flex-col gap-4">
                                <h3 class="font-bold text-lg">Welcome to DoReMiX</h3>
                                <p>A smarter way to manage YouTube playlists. <br />
                                    No clutter. No friction. No wasted time. <br />
                                    Just clean, powerful control.</p>
                            </div>
                            <Testimony name="Olivier De Jonckère" description="Teacher at Polytech Montpellier" testimony="DoReMix is one of the most secure applications I have ever seen. No injection vulnerabilities — I’m impressed." image="../../assets/images/profileimage.jpg" />
                        </div>
                        <Card image={null} title="Log in to DoReMiX" className="p-10 flex justify-center items-center rounded-b-lg lg:rounded-b-none lg:rounded-r-lg">
                            <form id="loginForm" class="mt-6 flex flex-col gap-5">
                                <Input id="email" placeholder="vincent.berry@umontpellier.fr" label="Email" type="email"></Input>
                                <div>
                                    <Input id="password" placeholder="*********" label="Password" type="password"></Input>
                                    <span id="togglePasswordVisibility" class="cursor-pointer text-xs text-muted-foreground">Show password</span>
                                </div>
                                <Button className="w-100 mt-5">Log in</Button>
                                <a href="/signup" class="text-center text-sm opacity-50">Sign up</a>
                            </form>
                        </Card>
                    </div>
                </div>
            }
        </div>
    );

    container.innerHTML = pageHtml;
    handleLogin();
    togglePasswordVisibility();

    function handleLogin() {
        const loginForm = document.getElementById('loginForm');

        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault()

            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);

            const email = data['email'].toString();
            const password = data['password'].toString();

            console.log(typeof (email))

            if (!email) {
                new AlertManager().error("Please enter your email address.");
                return;
            }

            if (!password) {
                new AlertManager().error("Please enter your password.");
                return;
            }

            if (!isValidEmail(email)) {
                new AlertManager().error("Please enter a valid email (@umontpellier.fr or @etu.umontpellier.fr).");
                return;
            }

            if (!isValidPassword(password)) {
                new AlertManager().error("Your password must be at least 8 characters and contains one uppercase, one lowercase, one digit and one special character.");
                return;
            }

            try {
                await authService.login(email, password);
                window.location.href = "/";
            } catch (e) {
                new AlertManager().error("Login failed. Please check your credentials.");
            }
            return

        })
    }

    function togglePasswordVisibility() {
        const btn = document.getElementById("togglePasswordVisibility")

        btn.addEventListener('click', () => {
            const passwordInput = document.getElementById("password")
            passwordInput.type == "password" ? passwordInput.type = "text" : passwordInput.type = "password"
        })
    }
}
