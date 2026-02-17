from __future__ import annotations

import typer

from src.services import auth_service
from src.utils.exceptions import (
    ApiRequestError,
    InvalidCredentialsError,
    InvalidRequestError,
    NotAuthenticatedError,
    UserExistsError,
)


app = typer.Typer(name="auth", help="Authentication commands.")


@app.command("register")
def register_command(
    email: str = typer.Option(..., "--email", prompt=True, help="University email."),
    password: str = typer.Option(
        ...,
        "--password",
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
    ),
) -> None:
    try:
        auth_service.register(email=email, password=password)
        typer.secho("Registration successful. You can now login.", fg="green")
    except UserExistsError as exc:
        typer.secho(str(exc), fg="yellow")
    except InvalidRequestError as exc:
        typer.secho(str(exc), fg="red")
    except ApiRequestError as exc:
        typer.secho(str(exc), fg="red")


@app.command("login")
def login_command(
    email: str = typer.Option(..., "--email", prompt=True, help="Account email."),
    password: str = typer.Option(..., "--password", prompt=True, hide_input=True),
) -> None:
    try:
        auth_service.login(email=email, password=password)
        typer.secho("Login successful.", fg="green")
    except InvalidCredentialsError as exc:
        typer.secho(str(exc), fg="red")
    except InvalidRequestError as exc:
        typer.secho(str(exc), fg="red")
    except ApiRequestError as exc:
        typer.secho(str(exc), fg="red")


@app.command("logout")
def logout_command() -> None:
    try:
        auth_service.logout()
        typer.secho("Logout successful.", fg="green")
    except NotAuthenticatedError as exc:
        typer.secho(str(exc), fg="yellow")
    except ApiRequestError as exc:
        typer.secho(str(exc), fg="red")
    except InvalidCredentialsError as exc:
        typer.secho(str(exc), fg="red")


@app.command("whoami")
def whoami_command() -> None:
    try:
        user = auth_service.whoami()
    except NotAuthenticatedError as exc:
        typer.secho(str(exc), fg="yellow")
        return
    except InvalidCredentialsError as exc:
        typer.secho(str(exc), fg="red")
        return
    except ApiRequestError as exc:
        typer.secho(str(exc), fg="red")
        return

    typer.secho("Authenticated user:", fg="cyan")
    typer.echo(f"  id: {user.get('id', 'N/A')}")
    typer.echo(f"  username: {user.get('username', 'N/A')}")
    typer.echo(f"  email: {user.get('email', 'N/A')}")
    typer.echo(f"  role: {user.get('role', 'N/A')}")
