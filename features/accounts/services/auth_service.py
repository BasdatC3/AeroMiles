from datetime import date

from main.db import execute_query, execute_write
from main.auth_utils import hash_password


def find_user_by_credentials(email, password):
    return execute_query(
        "SELECT email FROM pengguna WHERE email = %s AND password = %s",
        (email, hash_password(password)),
        fetch_one=True,
    )


def get_role(email):
    if execute_query("SELECT email FROM member WHERE email = %s", (email,), fetch_one=True):
        return 'member'
    if execute_query("SELECT email FROM staf WHERE email = %s", (email,), fetch_one=True):
        return 'staf'
    return None


def email_exists(email):
    return execute_query(
        "SELECT email FROM pengguna WHERE email = %s",
        (email,),
        fetch_one=True,
    ) is not None


def create_pengguna(data):
    execute_write(
        """INSERT INTO pengguna (email, password, salutation, first_mid_name, last_name,
           country_code, mobile_number, tanggal_lahir, kewarganegaraan)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            data['email'], hash_password(data['password']),
            data['salutation'], data['first_mid_name'], data['last_name'],
            data['country_code'], data['mobile_number'],
            data.get('tanggal_lahir') or None, data['kewarganegaraan'],
        ),
    )


def create_member(email, id_tier='T01'):
    execute_write(
        """INSERT INTO member (email, tanggal_bergabung, id_tier, award_miles, total_miles)
           VALUES (%s, %s, %s, 0, 0)""",
        (email, date.today(), id_tier),
    )


def create_staf(email, kode_maskapai):
    execute_write(
        "INSERT INTO staf (email, kode_maskapai) VALUES (%s, %s)",
        (email, kode_maskapai),
    )


def get_password(email):
    row = execute_query(
        "SELECT password FROM pengguna WHERE email = %s",
        (email,),
        fetch_one=True,
    )
    return row['password'] if row else None


def update_password(email, new_password):
    execute_write(
        "UPDATE pengguna SET password = %s WHERE email = %s",
        (hash_password(new_password), email),
    )
