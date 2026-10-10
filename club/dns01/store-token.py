#!/usr/bin/env python3
"""Masked terminal input; write only to Infisical, never to a local file."""
import getpass, sys, warnings
sys.dont_write_bytecode = True
from infisical_dns import Client, SafeError, private_process

def main():
    private_process()
    client = Client()
    client.ensure_folder()
    # An explicit terminal is mandatory: getpass must never fall back to echoed stdin.
    warnings.simplefilter("error", getpass.GetPassWarning)
    with open("/dev/tty", "w") as tty:
        if not tty.isatty():
            raise SafeError("Terminal interactif requis ; opération refusée.")
        value = getpass.getpass("Token Alwaysdata (saisie masquée) : ", stream=tty)
    if not value or not value.isascii() or any(c.isspace() for c in value) or ":" in value:
        raise SafeError("Token vide ou format invalide ; aucune valeur enregistrée.")
    length = client.store(value)
    print("Présent et relu : librechat-artefacts / prod /dns-hermione / "
          "ALWAYSDATA_API_TOKEN ; longueur : %d caractères. Valeur masquée." % length)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("Saisie annulée ; aucune valeur affichée.", file=sys.stderr)
        sys.exit(1)
    except Exception:
        print("Échec sécurisé ; aucune valeur ni réponse API affichée. "
              "Vérifier accès Infisical et terminal.", file=sys.stderr)
        sys.exit(1)
