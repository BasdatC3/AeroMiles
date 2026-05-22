from main.db import execute_query


def stats():
    def _count(query, params=None):
        row = execute_query(query, params, fetch_one=True)
        return row['cnt'] if row else 0

    total_miles = execute_query(
        "SELECT COALESCE(SUM(award_miles), 0) AS total FROM member",
        fetch_one=True,
    )

    return {
        'total_members': _count("SELECT COUNT(*) AS cnt FROM member"),
        'total_claims': _count("SELECT COUNT(*) AS cnt FROM claim_missing_miles"),
        'pending_claims': _count(
            "SELECT COUNT(*) AS cnt FROM claim_missing_miles WHERE status_penerimaan = 'Menunggu'"
        ),
        'approved_claims': _count(
            "SELECT COUNT(*) AS cnt FROM claim_missing_miles WHERE status_penerimaan = 'Disetujui'"
        ),
        'rejected_claims': _count(
            "SELECT COUNT(*) AS cnt FROM claim_missing_miles WHERE status_penerimaan = 'Ditolak'"
        ),
        'total_redeems': _count("SELECT COUNT(*) AS cnt FROM redeem"),
        'total_miles_beredar': total_miles['total'] if total_miles else 0,
    }


def recent_transactions(limit=30):
    items = []

    transfers = execute_query(
        """SELECT email_member_1, email_member_2, jumlah, catatan, timestamp
           FROM transfer ORDER BY timestamp DESC LIMIT 50""",
        fetch_all=True,
    ) or []
    for t in transfers:
        items.append({
            'tipe': 'Transfer',
            'member': t['email_member_1'],
            'detail': f"-> {t['email_member_2']}",
            'miles': t['jumlah'],
            'timestamp': t['timestamp'],
        })

    redeems = execute_query(
        """SELECT r.email_member, r.kode_hadiah, r.timestamp, h.miles, h.nama
           FROM redeem r LEFT JOIN hadiah h ON r.kode_hadiah = h.kode_hadiah
           ORDER BY r.timestamp DESC LIMIT 50""",
        fetch_all=True,
    ) or []
    for r in redeems:
        items.append({
            'tipe': 'Redeem',
            'member': r['email_member'],
            'detail': r['nama'] or r['kode_hadiah'],
            'miles': -(r['miles'] or 0),
            'timestamp': r['timestamp'],
        })

    packages = execute_query(
        """SELECT m.email_member, m.id_award_miles_package, m.timestamp, a.jumlah_award_miles
           FROM member_award_miles_package m
           LEFT JOIN award_miles_package a ON m.id_award_miles_package = a.id
           ORDER BY m.timestamp DESC LIMIT 50""",
        fetch_all=True,
    ) or []
    for p in packages:
        items.append({
            'tipe': 'Package',
            'member': p['email_member'],
            'detail': p['id_award_miles_package'],
            'miles': p['jumlah_award_miles'] or 0,
            'timestamp': p['timestamp'],
        })

    items.sort(key=lambda x: x['timestamp'], reverse=True)
    return items[:limit]


def top_members(limit=5):
    return execute_query(
        """SELECT m.email, m.nomor_member, m.total_miles, m.award_miles,
                  p.first_mid_name, p.last_name
           FROM member m JOIN pengguna p ON m.email = p.email
           ORDER BY m.total_miles DESC LIMIT %s""",
        (limit,), fetch_all=True,
    ) or []
