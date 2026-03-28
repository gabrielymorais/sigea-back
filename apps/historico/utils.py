"""
Utilitário para registrar ações no histórico.

Uso:
    from apps.historico.utils import registrar_acao
    from apps.historico.models import TipoAcao, Modulo

    registrar_acao(
        usuario=request.user,
        acao=TipoAcao.CRIAR,
        modulo=Modulo.ATAS,
        descricao='Criou a pasta "Reunião Março"',
        objeto_id=folder.pk,
        objeto_nome=folder.name,
    )
"""

from .models import HistoricoAcao, TipoAcao, Modulo


def registrar_acao(usuario, acao: str, modulo: str, descricao: str, objeto_id=None, objeto_nome=""):
    """Registra uma ação do usuário no histórico."""
    HistoricoAcao.objects.create(
        usuario=usuario,
        acao=acao,
        modulo=modulo,
        descricao=descricao,
        objeto_id=objeto_id,
        objeto_nome=objeto_nome or "",
    )
