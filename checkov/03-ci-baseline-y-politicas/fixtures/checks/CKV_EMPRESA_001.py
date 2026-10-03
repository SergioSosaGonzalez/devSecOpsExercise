# ============================================================
# Política interna de la empresa (Checkov no trae esta regla)
# ============================================================
# CKV_EMPRESA_001: todo bucket debe declarar su entorno con la
# etiqueta `Entorno`. Sin ella nadie sabe si el bucket es de
# producción o de pruebas, y acabas borrando el equivocado.
#
# Formato obligatorio desde Checkov 3.x: el check tiene que heredar
# de BaseResourceCheck e instanciarse al final del módulo. El
# formato antiguo que aparece en la documentación en línea
# (`def scan(resource_conf)` + `scan_resource_conf = scan`) ya no
# se carga: el escaneo termina con cero resultados y sin avisar.

from typing import Any, Dict, List

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

ETIQUETA_OBLIGATORIA = "Entorno"


class BucketConEntorno(BaseResourceCheck):
    def __init__(self) -> None:
        super().__init__(
            name="Ensure that S3 buckets declare the 'Entorno' tag",
            id="CKV_EMPRESA_001",
            categories=[CheckCategories.GENERAL_SECURITY],
            supported_resources=["aws_s3_bucket"],
        )

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        tags = conf.get("tags")
        if not tags:
            return CheckResult.FAILED

        # OJO: Checkov no te pasa las etiquetas como pares clave/valor
        # sueltos, sino como una lista que contiene UN diccionario:
        #   conf["tags"] == [{"Entorno": "produccion", "Owner": "finanzas"}]
        # Un `if "Entorno" in tags` aquí devuelve False siempre.
        etiquetas = {clave: valor for bloque in tags for clave, valor in bloque.items()}
        if ETIQUETA_OBLIGATORIA in etiquetas:
            return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["tags"]


check = BucketConEntorno()