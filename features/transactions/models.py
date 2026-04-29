from django.db import models


class ClaimMiles(models.Model):
    """Map to CLAIM_MISSING_MILES table - read only"""
    STATUS_CHOICES = [
        ('Menunggu', 'Menunggu'),
        ('Disetujui', 'Disetujui'),
        ('Ditolak', 'Ditolak'),
    ]
    KELAS_CHOICES = [
        ('Economy', 'Economy'),
        ('Business', 'Business'),
        ('First', 'First'),
    ]

    id = models.AutoField(primary_key=True)
    email_member = models.CharField(max_length=100)
    email_staf = models.CharField(max_length=100, null=True, blank=True)
    maskapai = models.CharField(max_length=10)
    bandara_asal = models.CharField(max_length=3)
    bandara_tujuan = models.CharField(max_length=3)
    tanggal_penerbangan = models.DateField()
    flight_number = models.CharField(max_length=10)
    nomor_tiket = models.CharField(max_length=20)
    kelas_kabin = models.CharField(max_length=20, choices=KELAS_CHOICES)
    pnr = models.CharField(max_length=10)
    status_penerimaan = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Menunggu')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'claim_missing_miles'
        managed = False

    def __str__(self):
        return f"{self.email_member} - {self.flight_number}"


class Transaction(models.Model):
    """Legacy - not used"""
    pass


class TransferMiles(models.Model):
    """Map to TRANSFER table - read only"""
    email_member_1 = models.CharField(max_length=100)
    email_member_2 = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    jumlah = models.IntegerField()
    catatan = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'transfer'
        managed = False

    def __str__(self):
        return f"{self.email_member_1} -> {self.email_member_2}: {self.jumlah}"