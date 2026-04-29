from django.db import models


class Reward(models.Model):
    """Map to HADIAH table - read only"""
    kode_hadiah = models.CharField(max_length=20, primary_key=True)
    nama = models.CharField(max_length=100)
    miles = models.IntegerField()
    deskripsi = models.TextField(blank=True)
    valid_start_date = models.DateField()
    program_end = models.DateField()

    class Meta:
        db_table = 'hadiah'
        managed = False

    def __str__(self):
        return f"{self.kode_hadiah} - {self.nama}"


class Redemption(models.Model):
    """Map to REDEEM table - read only"""
    email_member = models.CharField(max_length=100)
    kode_hadiah = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'redeem'
        managed = False

    def __str__(self):
        return f"{self.email_member} - {self.kode_hadiah}"


class Package(models.Model):
    """Map to AWARD_MILES_PACKAGE table - read only"""
    id = models.CharField(max_length=20, primary_key=True)
    harga_paket = models.DecimalField(max_digits=15, decimal_places=2)
    jumlah_award_miles = models.IntegerField()

    class Meta:
        db_table = 'award_miles_package'
        managed = False

    def __str__(self):
        return f"{self.id} - {self.jumlah_award_miles} miles"