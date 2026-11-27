"""Ponto de entrada do jogo.   Rodar no PC:   python main.py

Este arquivo fica na raiz do projeto porque a ferramenta pygbag (versão web,
para navegador e celular) exige um main.py aqui.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import app  # noqa: E402

# "python main.py --quadros 120" roda 120 quadros e fecha (usado nos testes)
limite = int(sys.argv[sys.argv.index("--quadros") + 1]) if "--quadros" in sys.argv else None
asyncio.run(app.principal(limite))
