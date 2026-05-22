from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """App config untuk fitur Accounts.

    Tidak mendefinisikan model ORM. Akses database menggunakan psycopg2 raw SQL
    melalui main.db (sesuai persyaratan TK03).
    """
    name = 'features.accounts'
    verbose_name = 'Accounts'
