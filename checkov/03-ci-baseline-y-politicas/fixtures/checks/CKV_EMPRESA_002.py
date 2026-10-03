# ============================================================
# Política interna de la empresa (Checkov no trae esta regla)
# ============================================================
# CKV_EMPRESA_002: los usuarios de base de datos no pueden llamarse
# como un administrador. Existe una cuenta de servicio
# (`svc_reporting`) que ya cubre los accesos privilegiados; si
# además hay un login llamado `*_admin`, ese login es la puerta
# que se ataca con las credenciales de la aplicación.

from typing import Any, Dict, List

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

SUFIJOS_PROHIBIDOS = ("_admin", "-admin", "-root")


class UsuarioNoAdministrador(BaseResourceCheck):
    def __init__(self) -> None:
        super().__init__(
            name="Ensure that DB usernames do not end with _admin or -admin",
            id="CKV_EMPRESA_002",
            categories=[CheckCategories.GENERAL_SECURITY],
            supported_resources=["aws_db_instance"],
        )

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        username = conf.get("username")
        if not username or not isinstance(username[0], str):
            return CheckResult.UNKNOWN

        if username[0].lower().endswith(SUFIJOS_PROHIBIDOS):
            return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ["username"]


check = UsuarioNoAdministrador()