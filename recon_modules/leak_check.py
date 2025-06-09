#!/usr/bin/env python
import sys, hashlib, requests, json, os

def main(email):
    # Exemplo: consulta rápida em "https://leak-checker-example.local/db.json"
    # Aqui só devolve hash SHA1 como demonstração.
    sha1 = hashlib.sha1(email.encode()).hexdigest().upper()
    print(json.dumps({"email": email, "sha1": sha1, "found": False}, indent=2))

if __name__ == "__main__":
    if len(sys.argv)<2:
        print("Uso: python leak_check.py <email>")
        sys.exit(1)
    main(sys.argv[1])
