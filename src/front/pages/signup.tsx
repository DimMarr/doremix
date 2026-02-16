import { Button, Input, AlertBox, Testimony } from "@components/generics";
import { AlertManager } from "@utils/alertManager";
import { isValidEmail, isValidPassword } from "@utils/authentication";
import { Card } from "@components/generics/card";

export async function SignupPage(container) {

    const pageHtml = (
        <div>
        {
            <div class="flex justify-center items-center h-[calc(100vh-64px)]">
                <div class="flex">
                    <div class="bg-(--color-secondary) rounded-l-lg p-10 w-md flex flex-col justify-between gap-10">
                        <div class="flex flex-col gap-4">
                            <h3 class="font-bold text-lg">Welcome to DoReMiX</h3>
                            <p>Lorem ipsum dolor sit amet consectetur, adipisicing elit. Totam aliquam dolores magni laborum doloribus, delectus natus sit saepe velit veniam odit optio omnis aliquid ad molestiae eaque. Nemo, animi possimus.</p>
                        </div>
                        <Testimony name="Olivier De Jonckère" description="Professeur en DO" testimony="DoReMix est une des applications les plus sécurisées qu'il m'est été donné de voir. Aucune injection, j'en suis impressionné." image="../../assets/images/profileimage.jpg"/>
                    </div>
                    <Card title="Sign up to DoReMiX" className="w-xl py-10 flex justify-center items-center rounded-l-none">
                        <form id="loginForm" class="mt-6 flex flex-col gap-5">
                            <Input id="email" placeholder="vincent.berry@umontpellier.fr" label="Email" type="email"></Input>
                            <div>
                                <Input id="password" placeholder="*********" label="Password" type="password"></Input>
                                <span id="togglePasswordVisibility" class="cursor-pointer text-xs text-muted-foreground">Show password</span>
                            </div>
                            <div>
                                <Input id="retypepassword" placeholder="*********" label="Retype Password" type="password"></Input>
                                <span id="toggleRetypePasswordVisibility" class="cursor-pointer text-xs text-muted-foreground">Show password</span>
                            </div>
                            <Button className="w-100 mt-5">Sign up</Button>
                            <a href="/login" class="text-center text-sm opacity-50">Log in</a>
                        </form>
                    </Card>
                </div>
            </div>
        }
        </div>
    );

    container.innerHTML = pageHtml;
    togglePasswordVisibility();

    function togglePasswordVisibility(){
        const btnPassword = document.getElementById("togglePasswordVisibility")
        const btnRetypePassword = document.getElementById("toggleRetypePasswordVisibility")

        btnPassword.addEventListener('click', () => {
            const passwordInput = document.getElementById("password")
            passwordInput.type == "password" ? passwordInput.type = "text" : passwordInput.type = "password"
        })

        btnRetypePassword.addEventListener('click', () => {
            const passwordInput = document.getElementById("retypepassword")
            passwordInput.type == "password" ? passwordInput.type = "text" : passwordInput.type = "password"
        })
    }
}
