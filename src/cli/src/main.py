from __future__ import annotations

import typer

from rich.console import Console

from src.commands.playlist import app as playlist_app
from src.commands.admin import admin_app
from src.commands.track import app as track_app
from src.commands.mod import app as mod_app
from src.commands.user import app as user_app

from src.services import auth_service
from src.utils.exceptions import (
    ApiRequestError,
    InvalidCredentialsError,
    InvalidRequestError,
    NotAuthenticatedError,
    UserExistsError,
)
from src.utils.token_storage import get_refresh_token

console = Console()
root_app = typer.Typer(help="DoReMix CLI.")


def _extract_error_detail(exc: Exception) -> str:
    message = str(exc).strip()
    if ": " in message:
        return message.split(": ", 1)[1].strip()
    return message


def _has_local_session() -> bool:
    try:
        _ = get_refresh_token()
        return True
    except NotAuthenticatedError:
        return False


def _verify_email_interactive(email: str) -> None:
    """Helper function to verify email interactively."""
    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        code = typer.prompt(
            "Enter the 6-digit verification code from your email", hide_input=False
        )

        # Validate code format
        if not code or len(code) != 6 or not code.isdigit():
            console.print(
                "[red]✗ Invalid code format. Please enter exactly 6 digits.[/red]"
            )
            if attempt < max_attempts:
                console.print(f"[yellow]Attempt {attempt}/{max_attempts}[/yellow]")
            continue

        try:
            auth_service.verify_email_code(email=email, code=code)
            console.print("[green]✓ Email verified successfully![/green]")
            console.print("[dim]You can now log in with your account.[/dim]")
            return
        except InvalidRequestError as exc:
            detail = _extract_error_detail(exc)
            if "expired" in detail.lower():
                console.print("[red]✗ Verification code has expired.[/red]")
                resend = typer.confirm(
                    "Would you like to resend the code?", default=True
                )
                if resend:
                    try:
                        auth_service.resend_verification_code(email)
                        console.print(
                            "[green]✓ New verification code sent to your email.[/green]"
                        )
                        attempt = 0  # Reset attempts
                        continue
                    except Exception as exc2:
                        console.print(
                            f"[red]✗ Failed to resend code: {_extract_error_detail(exc2)}[/red]"
                        )
                        return
                else:
                    return
            else:
                console.print(f"[red]✗ Verification failed: {detail}[/red]")
                if attempt < max_attempts:
                    console.print(f"[yellow]Attempt {attempt}/{max_attempts}[/yellow]")
        except InvalidCredentialsError as exc:
            console.print(f"[red]✗ Invalid code: {_extract_error_detail(exc)}[/red]")
            if attempt < max_attempts:
                console.print(f"[yellow]Attempt {attempt}/{max_attempts}[/yellow]")
        except ApiRequestError as exc:
            console.print(
                f"[red]✗ Verification error: {_extract_error_detail(exc)}[/red]"
            )
            return

    console.print(
        f"[red]✗ Maximum attempts ({max_attempts}) exceeded. Try registering again.[/red]"
    )


@root_app.command("register", help="Create a new account.")
def register_command(
    email: str | None = typer.Option(None, "--email", help="University email."),
    password: str | None = typer.Option(None, "--password", help="Account password."),
) -> None:
    if _has_local_session():
        console.print(
            "[yellow]You are already logged in. Run `doremix logout` before registering a new account.[/yellow]"
        )
        return

    if email is None:
        email = typer.prompt("Email")
    if password is None:
        password = typer.prompt("Password", hide_input=True, confirmation_prompt=True)

    try:
        auth_service.register(email=email, password=password)
        console.print(
            "[green]✓ Account created! A verification email has been sent to[/green] [bold]"
            + email
            + "[/bold]"
        )
        console.print("[dim]Please verify your email before logging in.[/dim]")

        # Prompt for email verification
        console.print()
        verify = typer.confirm("Do you want to verify your email now?", default=True)
        if verify:
            _verify_email_interactive(email)

    except UserExistsError:
        console.print(
            "[yellow]An account already exists for this email. Use `doremix login`.[/yellow]"
        )
    except InvalidRequestError as exc:
        detail = _extract_error_detail(exc)
        if "Invalid email format" in detail:
            console.print("[red]✗ Registration failed: invalid email format.[/red]")
            console.print(
                "[yellow]Use @umontpellier.fr or @etu.umontpellier.fr.[/yellow]"
            )
            return
        if "Password must be at least 8 characters" in detail:
            console.print("[red]✗ Registration failed: password is too weak.[/red]")
            console.print(
                "[yellow]Use at least 8 chars with uppercase, lowercase, digit, and special char.[/yellow]"
            )
            return
        console.print(f"[red]✗ Registration failed: {detail}[/red]")
    except ApiRequestError as exc:
        detail = _extract_error_detail(exc)
        console.print(f"[red]✗ Registration failed: {detail}[/red]")


@root_app.command("login", help="Authenticate and store local session tokens.")
def login_command(
    email: str | None = typer.Option(None, "--email", help="Account email."),
    password: str | None = typer.Option(None, "--password", help="Account password."),
) -> None:
    if _has_local_session():
        console.print(
            "[yellow]You are already logged in. Run `doremix logout` first.[/yellow]"
        )
        return

    if email is None:
        email = typer.prompt("Email")
    if password is None:
        password = typer.prompt("Password", hide_input=True)

    try:
        auth_service.login(email=email, password=password)
        console.print("[green]✓ Login successful.[/green]")
    except InvalidCredentialsError as exc:
        detail = _extract_error_detail(exc).lower()
        if "invalid credentials" in detail:
            console.print("[red]✗ Login failed: invalid email or password.[/red]")
            return
        if "banned" in detail:
            console.print("[red]✗ Login failed: this account is banned.[/red]")
            return
        if "verify your email" in detail:
            console.print("[red]✗ Login failed: your email is not verified yet.[/red]")
            return
        console.print(f"[red]✗ Login failed: {_extract_error_detail(exc)}[/red]")
    except InvalidRequestError as exc:
        console.print(f"[red]✗ Login failed: {_extract_error_detail(exc)}[/red]")
    except ApiRequestError as exc:
        console.print(f"[red]✗ Login failed: {_extract_error_detail(exc)}[/red]")


@root_app.command("logout", help="Logout and clear local session tokens.")
def logout_command() -> None:
    try:
        auth_service.logout()
        console.print("[green]✓ Logout successful.[/green]")
    except NotAuthenticatedError:
        console.print("[yellow]You are already logged out.[/yellow]")
    except InvalidCredentialsError as exc:
        console.print(
            f"[yellow]Session is no longer valid: {_extract_error_detail(exc)}[/yellow]"
        )
    except ApiRequestError as exc:
        console.print(f"[red]✗ Logout failed: {_extract_error_detail(exc)}[/red]")


@root_app.command("verify-email", help="Verify email with the code sent by email.")
def verify_email_command(
    email: str | None = typer.Option(None, "--email", help="Email address to verify."),
) -> None:
    if email is None:
        email = typer.prompt("Email address")

    _verify_email_interactive(email)


@root_app.command("whoami", help="Show the authenticated user.")
def whoami_command() -> None:
    try:
        user = auth_service.whoami()
    except NotAuthenticatedError:
        console.print("[yellow]You are not logged in. Use `doremix login`.[/yellow]")
        return
    except InvalidCredentialsError as exc:
        console.print(
            f"[red]✗ Unable to fetch user: {_extract_error_detail(exc)}[/red]"
        )
        return
    except ApiRequestError as exc:
        console.print(
            f"[red]✗ Unable to fetch user: {_extract_error_detail(exc)}[/red]"
        )
        return

    console.print("[cyan]Authenticated user:[/cyan]")
    console.print(f"  id: {user.get('id', 'N/A')}")
    console.print(f"  username: {user.get('username', 'N/A')}")
    console.print(f"  email: {user.get('email', 'N/A')}")
    console.print(f"  role: {user.get('role', 'N/A')}")


root_app.add_typer(playlist_app, name="playlist", help="Playlist commands.")
root_app.add_typer(track_app, name="track", help="Track commands.")
root_app.add_typer(admin_app, name="admin", help="Admin commands.")
root_app.add_typer(mod_app, name="mod", help="Moderator commands.")
root_app.add_typer(user_app, name="user", help="User management commands.")

app = root_app


def main() -> None:
    app()


if __name__ == "__main__":
    main()
