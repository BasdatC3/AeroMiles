from datetime import date

from main.db import execute_query, execute_write


def list_active_rewards():
    today = date.today()
    return execute_query(
        """SELECT * FROM hadiah
           WHERE valid_start_date <= %s AND program_end >= %s
           ORDER BY miles""",
        (today, today), fetch_all=True,
    ) or []


def get_member(email):
    return execute_query(
        "SELECT * FROM member WHERE email = %s",
        (email,), fetch_one=True,
    )


def get_hadiah(kode):
    return execute_query(
        "SELECT * FROM hadiah WHERE kode_hadiah = %s",
        (kode,), fetch_one=True,
    )


def is_within_period(hadiah):
    today = date.today()
    return hadiah['valid_start_date'] <= today <= hadiah['program_end']


def list_history(email):
    return execute_query(
        """SELECT r.kode_hadiah, r.timestamp, h.nama, h.miles
           FROM redeem r LEFT JOIN hadiah h ON r.kode_hadiah = h.kode_hadiah
           WHERE r.email_member = %s
           ORDER BY r.timestamp DESC""",
        (email,), fetch_all=True,
    ) or []


def execute_redeem(email, kode_hadiah, miles):
    execute_write(
        "UPDATE member SET award_miles = award_miles - %s WHERE email = %s",
        (miles, email),
    )
    execute_write(
        """INSERT INTO redeem (email_member, kode_hadiah, timestamp)
           VALUES (%s, %s, CURRENT_TIMESTAMP)""",
        (email, kode_hadiah),
    )
