"""
Helpers compartilhados para os testes do projeto.
"""
import itertools
from django.contrib.auth import get_user_model

User = get_user_model()
_counter = itertools.count(1)


def make_user(username=None, password="testpass123", is_staff=False, **kwargs):
    """Cria um usuário de teste com dados únicos gerados automaticamente."""
    n = next(_counter)
    username = username or f"user{n}"
    defaults = {
        "email": f"user{n}@test.com",
        "full_name": "Usuário Teste",
        "cpf": f"{n:03d}.{n:03d}.{n:03d}-{n:02d}",
        "telefone": "(85) 99999-9999",
        "tipo_profissional": "Professor",
        "escola_lotacao": "IFCE Teste",
        "portaria": "Portaria 001/2026",
        "is_staff": is_staff,
    }
    defaults.update(kwargs)
    return User.objects.create_user(username=username, password=password, **defaults)
