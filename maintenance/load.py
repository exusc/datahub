from organization.models import Owner, Environment
from django.utils.translation import gettext_lazy as _


class EnvironmentLoader():

    def load(self, request) -> str:
        """ Laden der Standard RTEs """
        def create(key, title, desc, natproc='', awlib='AW'):
            environment = Environment(
                owner = Owner.abx(), key=key, title=title, desc=desc,
                hostname='Q1.SYSTEMZ.ABRAXAS-ITS.CH', username='XXX', password='XXX',
                natproc=natproc, awlib=awlib
            )
            environment.save()

        create('PR', 'Prod', 'Produktion', natproc='NATAWPR')
        create('EN', 'Entw', 'Entwicklung', natproc='NATAWTE', awlib='AWE')
        create('T5', 'T5', 'Produktions-Test', natproc='NATAWTEP')
        create('TE', 'Test', 'Test', natproc='NATAWTE', awlib='AWE')
        create('AB', 'Abna', 'Abnahme', natproc='NATAWNAP')
        create('FU', 'FU', 'Fusion', natproc='NATAWT19')
        create('NK', 'NK', 'Neukunden', natproc='NATAWT12', )
        create('P9', 'PrTe', 'Produktion Tessin', natproc='NATAWP9', )
        create('TT', 'TT', 'Produktionstest Tessin', natproc='NATAWTIT', )
        create('PK', 'PrKS', 'KStA Produktion', natproc='NATAWPK', )

        return _('Environments successfully loaded')
