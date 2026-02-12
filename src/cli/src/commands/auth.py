from __future__ import annotations

import click

from src.services import auth_service
from src.utils.exceptions import (
    ApiRequestError,
    InvalidCredentialsError,
    InvalidRequestError,
    NotAuthenticatedError,
    UserExistsError,
)
from src.utils.token_storage import get_user


@click.group(name="auth")
def auth() -> None:
    """Authentication commands."""


@auth.command("register")
@click.option("--email", prompt=True, help="University email.")
@click.option("--username", prompt=True, help="Display username.")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def register_command(email: str, username: str, password: str) -> None:
    try:
        auth_service.register(email=email, password=password, username=username)
        click.secho("Registration successful. You are now logged in.", fg="green")
    except UserExistsError as exc:
        click.secho(str(exc), fg="yellow")
    except InvalidRequestError as exc:
        click.secho(str(exc), fg="red")
    except ApiRequestError as exc:
        click.secho(str(exc), fg="red")


@auth.command("login")
@click.option("--email", prompt=True, help="Account email.")
@click.option("--password", prompt=True, hide_input=True)
def login_command(email: str, password: str) -> None:
    try:
        auth_service.login(email=email, password=password)
        click.secho("Login successful.", fg="green")
    except InvalidCredentialsError as exc:
        click.secho(str(exc), fg="red")
    except InvalidRequestError as exc:
        click.secho(str(exc), fg="red")
    except ApiRequestError as exc:
        click.secho(str(exc), fg="red")


@auth.command("logout")
def logout_command() -> None:
    try:
        auth_service.logout()
        click.secho("Logout successful.", fg="green")
    except NotAuthenticatedError as exc:
        click.secho(str(exc), fg="yellow")
    except ApiRequestError as exc:
        click.secho(str(exc), fg="red")
    except InvalidCredentialsError as exc:
        click.secho(str(exc), fg="red")


@auth.command("whoami")
def whoami_command() -> None:
    try:
        user = get_user()
    except NotAuthenticatedError as exc:
        click.secho(str(exc), fg="yellow")
        return

    click.secho("Authenticated user:", fg="cyan")
    click.echo(f"  id: {user.get('id', 'N/A')}")
    click.echo(f"  username: {user.get('username', 'N/A')}")
    click.echo(f"  email: {user.get('email', 'N/A')}")
    click.echo(f"  role: {user.get('role', 'N/A')}")
