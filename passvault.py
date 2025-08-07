import os
import json
import base64
import pyperclip
from cryptography.fernet import Fernet, InvalidToken
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from getpass import getpass



# === GLOBALS ===
VAULT_FILE = 'vault.dat'
console = Console()

# === KEY GENERATION ===
def generate_key(master_password: str) -> bytes:
    """Generate a Fernet-compatible key from a master password."""
    return base64.urlsafe_b64encode(master_password.ljust(32)[:32].encode())

# === MAIN VAULT CLASS ===
class PassVault:
    def __init__(self, master_password: str):
        self.key = generate_key(master_password)
        self.fernet = Fernet(self.key)
        self.data = {}

        if os.path.exists(VAULT_FILE):
            with open(VAULT_FILE, 'rb') as file:
                encrypted = file.read()
                try:
                    decrypted = self.fernet.decrypt(encrypted)
                    self.data = json.loads(decrypted)
                except InvalidToken:
                    console.print("[bold red]❌ Invalid master password. Access denied.[/bold red]")
                    exit(1)

    def save(self):
        """Encrypt and save the vault."""
        encrypted = self.fernet.encrypt(json.dumps(self.data).encode())
        with open(VAULT_FILE, 'wb') as file:
            file.write(encrypted)

    def add_entry(self, site, username, password):
        """Add or update an entry in the vault."""
        self.data[site] = {'username': username, 'password': password}
        self.save()
        console.print(f"[green]✅ Entry for '{site}' added successfully.[/green]")

    def get_entry(self, site):
        """Retrieve a password entry."""
        if site in self.data:
            username = self.data[site]['username']
            password = self.data[site]['password']

            table = Table(title=f"🔍 Entry for [cyan]{site}[/cyan]")
            table.add_column("Field", style="bold")
            table.add_column("Value")
            table.add_row("Username", username)
            table.add_row("Password", password)
            console.print(table)

            # ✅ COPY TO CLIPBOARD
            pyperclip.copy(password)
            console.print("[green]📋 Password copied to clipboard![/green]")
        else:
            console.print(f"[red]❌ No entry found for '{site}'.[/red]")

    def delete_entry(self, site):
        """Delete an entry from the vault."""
        if site in self.data:
            del self.data[site]
            self.save()
            console.print(f"[yellow]🗑️ Entry for '{site}' deleted.[/yellow]")
        else:
            console.print(f"[red]❌ No entry found for '{site}'.[/red]")

# === CLI MENU ===
def main():
    console.print("[bold cyan]🔐 Welcome to PassVault - Your Local Encrypted Vault[/bold cyan]")
    master = getpass("Enter your master password: ")
    vault = PassVault(master)

    while True:
        console.print("\n[bold]📋 Options:[/bold]")
        console.print("[1] Add Entry\n[2] Get Entry\n[3] Delete Entry\n[4] Exit")

        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4"], default="4")

        if choice == '1':
            input_site = Prompt.ask("Site name").strip()
            input_username = Prompt.ask("Username").strip()
            input_password = getpass("Password: ")
            vault.add_entry(input_site, input_username, input_password)

        elif choice == '2':
            input_site = Prompt.ask("Site name").strip()
            vault.get_entry(input_site)

        elif choice == '3':
            input_site = Prompt.ask("Site name").strip()
            vault.delete_entry(input_site)

        elif choice == '4':
            console.print("[bold green]👋 Goodbye! Your vault is safe.[/bold green]")
            break

if __name__ == "__main__":
    main()
