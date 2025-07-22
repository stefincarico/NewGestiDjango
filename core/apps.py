from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        Questo metodo viene eseguito da Django quando l'applicazione è pronta.
        È il posto standard per importare e quindi registrare i segnali.
        """
        import core.signals