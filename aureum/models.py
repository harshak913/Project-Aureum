# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Balance(models.Model):
    accession_number = models.ForeignKey('Scrape', models.DO_NOTHING, db_column='accession_number')
    member = models.CharField(max_length=500, blank=True, null=True)
    header = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=5000, blank=True, null=True)
    acc_name = models.CharField(max_length=5000, blank=True, null=True)
    value = models.CharField(max_length=500, blank=True, null=True)
    unit = models.CharField(max_length=500, blank=True, null=True)
    year = models.DateField(blank=True, null=True)
    statement = models.CharField(max_length=500, blank=True, null=True)
    report_period = models.DateField(blank=True, null=True)
    filing_type = models.CharField(max_length=45, blank=True, null=True)
    months_ended = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'balance'


class CashFlow(models.Model):
    accession_number = models.ForeignKey('Scrape', models.DO_NOTHING, db_column='accession_number')
    member = models.CharField(max_length=500, blank=True, null=True)
    header = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=5000, blank=True, null=True)
    acc_name = models.CharField(max_length=5000, blank=True, null=True)
    value = models.CharField(max_length=500, blank=True, null=True)
    unit = models.CharField(max_length=500, blank=True, null=True)
    year = models.DateField(blank=True, null=True)
    statement = models.CharField(max_length=500, blank=True, null=True)
    report_period = models.DateField(blank=True, null=True)
    filing_type = models.CharField(max_length=45, blank=True, null=True)
    months_ended = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cash_flow'


class Company(models.Model):
    cik = models.IntegerField(primary_key=True)
    ticker = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=445, blank=True, null=True)
    classification = models.IntegerField(blank=True, null=True)
    classification_name = models.CharField(max_length=250, blank=True, null=True)
    description = models.CharField(max_length=10000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'company'


class Dictionary(models.Model):
    standard_name = models.CharField(max_length=5000, blank=True, null=True)
    eng_name = models.CharField(max_length=5000, blank=True, null=True)
    acc_name = models.CharField(max_length=5000, blank=True, null=True)
    statement = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dictionary'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Income(models.Model):
    accession_number = models.ForeignKey('Scrape', models.DO_NOTHING, db_column='accession_number')
    member = models.CharField(max_length=500, blank=True, null=True)
    header = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=5000, blank=True, null=True)
    acc_name = models.CharField(max_length=5000, blank=True, null=True)
    value = models.CharField(max_length=500, blank=True, null=True)
    unit = models.CharField(max_length=500, blank=True, null=True)
    year = models.DateField(blank=True, null=True)
    statement = models.CharField(max_length=500, blank=True, null=True)
    report_period = models.DateField(blank=True, null=True)
    filing_type = models.CharField(max_length=45, blank=True, null=True)
    months_ended = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'income'


class MasterIdx(models.Model):
    master_file = models.CharField(max_length=25, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'master_idx'


class NonStatement(models.Model):
    accession_number = models.ForeignKey('Scrape', models.DO_NOTHING, db_column='accession_number')
    member = models.CharField(max_length=500, blank=True, null=True)
    header = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=5000, blank=True, null=True)
    acc_name = models.CharField(max_length=5000, blank=True, null=True)
    value = models.CharField(max_length=500, blank=True, null=True)
    unit = models.CharField(max_length=500, blank=True, null=True)
    year = models.DateField(blank=True, null=True)
    statement = models.CharField(max_length=500, blank=True, null=True)
    report_period = models.DateField(blank=True, null=True)
    filing_type = models.CharField(max_length=45, blank=True, null=True)
    months_ended = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'non_statement'


class Scrape(models.Model):
    cik = models.ForeignKey(Company, models.DO_NOTHING)
    filing_type = models.CharField(max_length=45, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    file_name = models.CharField(max_length=445, blank=True, null=True)
    accession_number = models.CharField(primary_key=True, max_length=445)
    inter_or_htm = models.CharField(max_length=5, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    quarter = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'scrape'


class StandardBalance(models.Model):
    accession_number = models.ForeignKey(Scrape, models.DO_NOTHING, db_column='accession_number')
    header = models.CharField(max_length=5000, blank=True, null=True)
    standard_name = models.CharField(max_length=5000, blank=True, null=True)
    eng_name = models.CharField(max_length=5000, blank=True, null=True)
    acc_name = models.CharField(max_length=5000, blank=True, null=True)
    value = models.CharField(max_length=500, blank=True, null=True)
    unit = models.CharField(max_length=500, blank=True, null=True)
    year = models.DateField(blank=True, null=True)
    statement = models.CharField(max_length=500, blank=True, null=True)
    report_period = models.DateField(blank=True, null=True)
    filing_type = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'standard_balance'


class StandardCash(models.Model):
    accession_number = models.ForeignKey(Scrape, models.DO_NOTHING, db_column='accession_number')
    header = models.CharField(max_length=5000, blank=True, null=True)
    standard_name = models.CharField(max_length=5000, blank=True, null=True)
    eng_name = models.CharField(max_length=5000, blank=True, null=True)
    acc_name = models.CharField(max_length=5000, blank=True, null=True)
    value = models.CharField(max_length=500, blank=True, null=True)
    unit = models.CharField(max_length=500, blank=True, null=True)
    year = models.DateField(blank=True, null=True)
    statement = models.CharField(max_length=500, blank=True, null=True)
    report_period = models.DateField(blank=True, null=True)
    filing_type = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'standard_cash'


class StandardDict(models.Model):
    standard_name = models.CharField(max_length=5000, blank=True, null=True)
    acc_name = models.CharField(max_length=5000, blank=True, null=True)
    statement = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'standard_dict'


class StandardIncome(models.Model):
    accession_number = models.ForeignKey(Scrape, models.DO_NOTHING, db_column='accession_number')
    header = models.CharField(max_length=5000, blank=True, null=True)
    standard_name = models.CharField(max_length=5000, blank=True, null=True)
    eng_name = models.CharField(max_length=5000, blank=True, null=True)
    acc_name = models.CharField(max_length=5000, blank=True, null=True)
    value = models.CharField(max_length=500, blank=True, null=True)
    unit = models.CharField(max_length=500, blank=True, null=True)
    year = models.DateField(blank=True, null=True)
    statement = models.CharField(max_length=500, blank=True, null=True)
    report_period = models.DateField(blank=True, null=True)
    filing_type = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'standard_income'
