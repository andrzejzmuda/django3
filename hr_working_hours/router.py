class TimeRegistryRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'time_registry':
            return 'default'
        return None
    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to app1.
        """
        if model._meta.app_label == 'time_registry':
            return 'time_registry'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        All non-auth models end up in this pool.
        """
        return True
