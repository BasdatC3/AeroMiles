from main.db import execute_query, execute_write


def member_balance(email):
    return execute_query(
        "SELECT award_miles FROM member WHERE email = %s",
        (email,), fetch_one=True,
    )


def member_exists(email):
    return execute_query(
        "SELECT email FROM member WHERE email = %s",
        (email,), fetch_one=True,
    ) is not None


def list_history(email):
    sent = execute_query(
        """SELECT email_member_1 AS me, email_member_2 AS counterpart,
                  jumlah, catatan, timestamp, 'Kirim' AS tipe
           FROM transfer WHERE email_member_1 = %s""",
        (email,), fetch_all=True,
    ) or []
    received = execute_query(
        """SELECT email_member_2 AS me, email_member_1 AS counterpart,
                  jumlah, catatan, timestamp, 'Terima' AS tipe
           FROM transfer WHERE email_member_2 = %s""",
        (email,), fetch_all=True,
    ) or []
    return sorted(sent + received, key=lambda x: x['timestamp'], reverse=True)


def execute_transfer(from_email, to_email, jumlah, catatan):
    execute_write(
        "UPDATE member SET award_miles = award_miles - %s WHERE email = %s",
        (jumlah, from_email),
    )
    execute_write(
        "UPDATE member SET award_miles = award_miles + %s WHERE email = %s",
        (jumlah, to_email),
    )
    execute_write(
        """INSERT INTO transfer (email_member_1, email_member_2, jumlah, catatan, timestamp)
           VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)""",
        (from_email, to_email, jumlah, catatan),
    )
