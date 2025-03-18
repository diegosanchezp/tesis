from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class EgresadosData(models.Model):
    """ """

    class PrefijoCedula(models.TextChoices):
        VENEZOLANO = "VENEZOLANO", _("Venezolano")
        PASAPORTE = "PASAPORTE", _("Pasaporte")
        JURÍDICO = "JURÍDICO", _("Jurídico")
        EXTRANJERO = "EXTRANJERO", _("Extranjero")
        GUBERNAMENTAL = "GUBERNAMENTAL", _("Gubernamental")
        COMUNA = "COMUNA", _("Comuna")

    prefijo_cedula = models.CharField(
        max_length=255,
        choices=PrefijoCedula.choices,
        verbose_name=_("Prefijo cédula"),
        help_text=_(""),
    )

    cedula = models.PositiveIntegerField(
        verbose_name=_("Cédula"),
        help_text=_(""),
    )

    nombre = models.CharField(
        max_length=255,
        verbose_name=_("Nombre"),
        help_text=_(""),
    )

    segundo_nombre = models.CharField(
        max_length=255,
        verbose_name=_("Segundo Nombre"),
        help_text=_(""),
    )

    apellido = models.CharField(
        max_length=255,
        verbose_name=_("Apellido"),
        help_text=_(""),
    )

    segundo_apellido = models.CharField(
        max_length=255,
        verbose_name=_("Segundo Apellido"),
        help_text=_(""),
    )

    fecha_nac = models.DateField(
        verbose_name=_("Fecha nacimiento"),
        help_text=_(""),
    )

    ciudad = models.CharField(
        max_length=255,
        verbose_name=_("Ciudad"),
        help_text=_(""),
    )

    pais_nac = models.CharField(
        max_length=255,
        verbose_name=_("Pais nacimiento"),
        help_text=_(""),
    )

    estado = models.CharField(
        max_length=255,
        verbose_name=_("Estado"),
        help_text=_(""),
    )

    direccion = models.CharField(
        max_length=255,
        verbose_name=_("Direccion"),
        help_text=_(""),
    )

    telefono_2 = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Telefono 2"),
        help_text=_(""),
    )

    class Sexo(models.TextChoices):
        MASCULINO = "M", _("Masculino")
        FEMENINO = "F", _("Femenino")

    sexo = models.CharField(
        choices=Sexo.choices,
        max_length=255,
        verbose_name=_("Sexo"),
        help_text=_(""),
    )

    usuario = models.CharField(
        max_length=255,
        verbose_name=_("Usuario"),
        help_text=_(""),
    )

    idafiliados = models.PositiveIntegerField(
        verbose_name=_("Idafiliados"),
        help_text=_(""),
    )

    carnet = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Carnet"),
        help_text=_(""),
    )

    email = models.EmailField(
        verbose_name=_("Email"),
        help_text=_(""),
    )

    telefono = models.CharField(
        max_length=255,
        verbose_name=_("Telefono"),
        help_text=_(""),
    )

    celular = models.CharField(
        verbose_name=_("Celular"),
        help_text=_(""),
    )

    fec_registro = models.DateField(
        verbose_name=_("Fecha Registro"),
        help_text=_(""),
    )

    fec_afiliacion = models.DateField(
        verbose_name=_("Fecha Afiliacion"),
        null=True,
        blank=True,
        help_text=_(""),
    )

    class Estatus(models.TextChoices):
        SIN_CARNET = "0", _("Sin carnet")
        ACTIVO = "1", _("Activo")
        OTROS = "otros", _("Otros")

    # maybe an internal field that shouldn't be exposed in the form ?
    estatus = models.CharField(
        verbose_name=_("Estatus"),
        choices=Estatus.choices,
        null=True,
        blank=True,
        help_text=_(""),
    )

    pais = models.CharField(
        max_length=255,
        verbose_name=_("Pais"),
        help_text=_(""),
    )

    tipo_afiliacion = models.CharField(
        max_length=255,
        verbose_name=_("Tipo Afiliacion"),
        help_text=_(""),
    )

    codigo_postal = models.PositiveIntegerField(
        verbose_name=_("Codigo postal"),
        help_text=_(""),
    )

    empleado_ucv = models.BooleanField(
        default=False,
        verbose_name=_("Empleado ucv"),
        help_text=_(""),
    )

    fac_empleado = models.CharField(
        max_length=255,
        verbose_name=_("Facultad Empleado"),
        help_text=_(""),
    )

    otra_dependencia = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name=_("Otra dependencia"),
        help_text=_(""),
    )

    fecha_ingreso = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Fecha Ingreso"),
        help_text=_(""),
    )

    egresado_pregrado_ucv = models.CharField(
        max_length=255,
        verbose_name=_("Egresado pregrado ucv"),
        help_text=_(""),
    )

    titulo_pregrado_ucv = models.CharField(
        max_length=255,
        verbose_name=_("Titulo pregrado ucv"),
        help_text=_(""),
    )

    universidad_pregrado_otra = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Universidad pregrado otra"),
        help_text=_(""),
    )

    fecha_egreso_pregrado_otra = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Fecha egreso pregrado otra"),
        help_text=_(""),
    )

    facultad_postgrado_ucv = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Facultad postgrado ucv"),
        help_text=_(""),
    )

    programa_postgrado = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Programa postgrado"),
        help_text=_(""),
    )

    otro_pregrado = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        verbose_name=_("Otro pregrado"),
        help_text=_(""),
    )

    titulo_postgrado_ucv = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Titulo postgrado ucv"),
        help_text=_(""),
    )

    fecha_egreso_postgrado_ucv = models.DateField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Fecha egreso postgrado ucv"),
        help_text=_(""),
    )

    universidad_postgrado_otra = models.BooleanField(
        default=False,
        verbose_name=_("Universidad postgrado otra"),
        help_text=_(""),
    )

    fecha_egreso_postgrado_otra = models.DateField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Fecha egreso postgrado otra"),
        help_text=_(""),
    )

    monto_aporte = models.CharField(
        verbose_name=_("Monto aporte"),
        help_text=_(""),
    )

    titulo_postgrado_otra = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Titulo postgrado otra"),
        help_text=_(""),
    )

    empresa = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("empresa"),
        help_text=_(""),
    )

    sector = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Sector"),
        help_text=_(""),
    )

    solicitar_seguro = models.BooleanField(
        default=False,
        verbose_name=_("Solicitar seguro"),
        help_text=_(""),
    )

    egresado_postgrado_ucv = models.BooleanField(
        default=False,
        verbose_name=_("Egresado postgrado ucv"),
        help_text=_(""),
    )

    medios_sociales = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Medios sociales"),
        help_text=_(""),
    )

    titulo_pregrado_otra = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Titulo pregrado otra"),
        help_text=_(""),
    )

    fecha_egreso_pregrado_ucv = models.DateField(
        max_length=255,
        verbose_name=_("Fecha egreso pregrado ucv"),
        help_text=_(""),
    )

    facultad_pregrado_ucv = models.CharField(
        max_length=255,
        verbose_name=_("Facultad pregrado ucv"),
        help_text=_(""),
    )

    empleado_externo = models.BooleanField(
        default=False,
        max_length=255,
        verbose_name=_("Empleado externo"),
        help_text=_(""),
    )

    pais_donde_trabaja = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Pais donde trabaja"),
        help_text=_(""),
    )

    solicitar_td_caroni = models.BooleanField(
        default=False,
        verbose_name=_("Solicitar TD Caroni"),
        help_text=_(""),
    )

    def __str__(self):
        return f"{self.nombre} {self.cedula}"

    class Meta:
        verbose_name = _("Data Egresado")
        unique_together = [["cedula", "prefijo_cedula"]]
        verbose_name_plural = _("Data Egresados")
