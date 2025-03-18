from django.db.utils import IntegrityError
from datetime import date
from pathlib import Path

from django_src.test_utils import parse_test_data_args
from shscripts.backup import setup_django


class EgresadosTestData:
    """
    Life cyle (the order you should call the methods)
    1. create
    2. get <-- get the created data
    3. delete
    """

    def __init__(self):
        from django_src.egresados_update.models import EgresadosData

        self.EgresadosData = EgresadosData

        self.egresado_data_1 = EgresadosData(
            prefijo_cedula=EgresadosData.PrefijoCedula.VENEZOLANO,
            cedula=123456,
            nombre="José",
            segundo_nombre="María",
            apellido="Vargas",
            segundo_apellido="Ponce",
            fecha_nac=date(year=1786, month=3, day=10),
            ciudad="Caracas",
            pais_nac="Venezuela",
            estado="Miranda",
            direccion="Estado Vargas, Municipio ...",
            telefono_2=None,
            sexo=EgresadosData.Sexo.MASCULINO,
            usuario="jose_vargas",
            idafiliados=10450,
            carnet=None,
            email="jose_vargas@ucv.ve",
            telefono="582121234567",
            celular="584141234567",
            fec_registro=date(year=2025, month=3, day=10),
            fec_afiliacion=None,
            estatus=EgresadosData.Estatus.SIN_CARNET,
            pais="Venezuela",
            tipo_afiliacion="Egresado",
            codigo_postal="1080",
            empleado_ucv=True,
            fac_empleado="Facultad de Medicina",
            otra_dependencia=None,
            fecha_ingreso=None,
            egresado_pregrado_ucv=True,
            titulo_pregrado_ucv="Cirujano",
            universidad_pregrado_otra="",
            fecha_egreso_pregrado_otra=None,
            facultad_postgrado_ucv="Facultad de Medicina",
            programa_postgrado="Maestría",
            otro_pregrado=False,
            titulo_postgrado_ucv="Doctor en medicina",
            fecha_egreso_postgrado_ucv=date(year=1816, month=3, day=10),
            universidad_postgrado_otra=False,
            fecha_egreso_postgrado_otra=None,
            monto_aporte="Basica",
            titulo_postgrado_otra=None,
            empresa="",
            sector="Medicina",
            solicitar_seguro=False,
            egresado_postgrado_ucv=True,
            medios_sociales="Amigo",
            titulo_pregrado_otra="",
            fecha_egreso_pregrado_ucv=date(year=1812, month=7, day=12),
            facultad_pregrado_ucv="Facultad de Medicina",
            empleado_externo=False,
            pais_donde_trabaja="",
            solicitar_td_caroni=False,
        )

    def get_egresado(self, egresados_data):
        egresados_data_db = self.EgresadosData.objects.get(
            cedula=egresados_data.cedula, prefijo_cedula=egresados_data.prefijo_cedula
        )
        return egresados_data_db

    def save_egresado_data(self, egresados_data):

        try:
            egresados_data.save()
        except IntegrityError as integrity_error:

            if "unique constraint" in integrity_error.args[0]:

                print(
                    egresados_data, "already exists deleting it and creating it again."
                )

                # if the user already exists, delete it and create it again
                egresados_data_db = self.EgresadosData.objects.get(
                    cedula=egresados_data.cedula,
                    prefijo_cedula=egresados_data.prefijo_cedula,
                )
                egresados_data_db.delete()
                egresados_data.save()

    def create(self):
        self.save_egresado_data(self.egresado_data_1)

    def get(self):
        self.egresado_data_1 = self.get_egresado(self.egresado_data_1)

    def delete(self):
        self.get()
        self.egresado_data_1.delete()


# python -m django_src.egresados_update.test_data.egresados_data --action create
# python -m django_src.egresados_update.test_data.egresados_data --action delete
if __name__ == "__main__":

    setup_django(".")
    args = parse_test_data_args()
    egresados_test_data = EgresadosTestData()

    if args.action == "create":
        egresados_test_data.create()
    elif args.action == "delete":
        egresados_test_data.delete()
