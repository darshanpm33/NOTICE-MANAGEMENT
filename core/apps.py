from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Patch Djongo to disable RETURNING in INSERT and other problematic features
        from django.db import connections
        from djongo.base import DatabaseFeatures
        
        # Monkey patch the class itself to be sure
        DatabaseFeatures.can_return_columns_from_insert = False
        DatabaseFeatures.can_return_rows_from_bulk_insert = False
        DatabaseFeatures.has_select_for_update = False
        
        try:
            for conn in connections.all():
                if conn.vendor == 'djongo':
                    conn.features.can_return_columns_from_insert = False
                    conn.features.can_return_rows_from_bulk_insert = False
                    conn.features.has_select_for_update = False
        except Exception:
            pass
