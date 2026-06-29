#!/usr/bin/env python3
import secrets
import string

longitud = 64
caracteres = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
secreto = "".join(secrets.choice(caracteres) for _ in range(longitud))

print(secreto)
