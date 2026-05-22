from datetime import datetime

from main.db import execute_query


def member_recent_transactions(email, limit=5):
    """Gabungan klaim, transfer, redeem, package — diurutkan terbaru."""
    items = []

    claims = execute_query(
        """SELECT id, maskapai, bandara_asal, bandara_tujuan, tanggal_penerbangan,
                  flight_number, status_penerimaan, timestamp
           FROM claim_missing_miles
           WHERE email_member = %s
           ORDER BY timestamp DESC LIMIT %s""",
        (email, limit), fetch_all=True,
    ) or []
    for c in claims:
        items.append({
            'type': 'Klaim',
            'description': f"{c['maskapai']} {c['bandara_asal']}->{c['bandara_tujuan']}",
            'amount': 0,
            'status': c['status_penerimaan'],
            'timestamp': c['timestamp'],
        })

    sent = execute_query(
        """SELECT email_member_2, jumlah, timestamp
           FROM transfer WHERE email_member_1 = %s
           ORDER BY timestamp DESC LIMIT %s""",
        (email, limit), fetch_all=True,
    ) or []
    for t in sent:
        items.append({
            'type': 'Transfer',
            'description': f"Kirim ke {t['email_member_2']}",
            'amount': -t['jumlah'],
            'status': 'Selesai',
            'timestamp': t['timestamp'],
        })

    received = execute_query(
        """SELECT email_member_1, jumlah, timestamp
           FROM transfer WHERE email_member_2 = %s
           ORDER BY timestamp DESC LIMIT %s""",
        (email, limit), fetch_all=True,
    ) or []
    for t in received:
        items.append({
            'type': 'Transfer',
            'description': f"Terima dari {t['email_member_1']}",
            'amount': t['jumlah'],
            'status': 'Selesai',
            'timestamp': t['timestamp'],
        })

    redeems = execute_query(
        """SELECT r.kode_hadiah, r.timestamp, h.nama, h.miles
           FROM redeem r LEFT JOIN hadiah h ON r.kode_hadiah = h.kode_hadiah
           WHERE r.email_member = %s
           ORDER BY r.timestamp DESC LIMIT %s""",
        (email, limit), fetch_all=True,
    ) or []
    for r in redeems:
        items.append({
            'type': 'Redeem',
            'description': r['nama'] or r['kode_hadiah'],
            'amount': -(r['miles'] or 0),
            'status': 'Selesai',
            'timestamp': r['timestamp'],
        })

    packages = execute_query(
        """SELECT m.id_award_miles_package, m.timestamp, a.jumlah_award_miles
           FROM member_award_miles_package m
           LEFT JOIN award_miles_package a ON m.id_award_miles_package = a.id
           WHERE m.email_member = %s
           ORDER BY m.timestamp DESC LIMIT %s""",
        (email, limit), fetch_all=True,
    ) or []
    for p in packages:
        items.append({
            'type': 'Package',
            'description': p['id_award_miles_package'],
            'amount': p['jumlah_award_miles'] or 0,
            'status': 'Selesai',
            'timestamp': p['timestamp'],
        })

    items.sort(key=lambda x: x['timestamp'] or datetime.min, reverse=True)
    return items[:limit]


def staff_claim_summary(staff_email):
    waiting = execute_query(
        "SELECT COUNT(*) AS cnt FROM claim_missing_miles WHERE status_penerimaan = 'Menunggu'",
        fetch_one=True,
    )
    approved = execute_query(
        """SELECT COUNT(*) AS cnt FROM claim_missing_miles
           WHERE email_staf = %s AND status_penerimaan = 'Disetujui'""",
        (staff_email,), fetch_one=True,
    )
    rejected = execute_query(
        """SELECT COUNT(*) AS cnt FROM claim_missing_miles
           WHERE email_staf = %s AND status_penerimaan = 'Ditolak'""",
        (staff_email,), fetch_one=True,
    )
    return {
        'menunggu': waiting['cnt'] if waiting else 0,
        'disetujui': approved['cnt'] if approved else 0,
        'ditolak': rejected['cnt'] if rejected else 0,
    }
