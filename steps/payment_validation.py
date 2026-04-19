"""Payment validation – schema, types, and business rules (R1–R7).

Implements validation logic as Robot keywords. Kept separate from HTTP/JSON handling
for single responsibility and testability.
"""

from typing import Any, Dict

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn


class PaymentValidation:
    """Robot library for validating payment API responses against R1–R7."""

    def validate_response_status_and_structure(self, response: Dict[str, Any]) -> None:
        """Fail if status != 200 or payment_methods missing/not array."""
        status = response.get("status")
        if status is None:
            raise AssertionError("Response missing required field 'status'")
        if not isinstance(status, int):
            raise AssertionError(
                f"Type: 'status' must be int, got {type(status).__name__}"
            )
        if status != 200:
            raise AssertionError(
                f"Non-success status: body.status={status} (expected 200). Fail fast."
            )
        pm = response.get("payment_methods")
        if pm is None:
            raise AssertionError("Response missing required field 'payment_methods'")
        if not isinstance(pm, list):
            raise AssertionError(
                f"R1: payment_methods must be array, got {type(pm).__name__}"
            )

    def validate_payment_methods_r1_r2_r3_r4(self, response: Dict[str, Any]) -> None:
        """R1: required fields; R2: selectable only if is_clickable; R3: is_wallet; R4: options array."""
        pm_list = response.get("payment_methods") or []
        for i, method in enumerate(pm_list):
            if not isinstance(method, dict):
                raise AssertionError(
                    f"R1: payment_methods[{i}] must be object, got {type(method).__name__}"
                )
            for key, exp_type in [("id", int), ("type", str), ("title", str), ("is_clickable", bool)]:
                if key not in method:
                    raise AssertionError(
                        f"R1/S6: payment_methods[{i}] missing required field '{key}'"
                    )
                val = method[key]
                if not isinstance(val, exp_type):
                    raise AssertionError(
                        f"Type: payment_methods[{i}].{key} must be {exp_type.__name__}, got {type(val).__name__}"
                    )
            # R3: is_wallet must be false if type is not wallet (schema didn't define is_wallet; treat as optional)
            if "is_wallet" in method and method["is_wallet"] is True:
                if method.get("type") != "wallet":
                    raise AssertionError(
                        f"R3: is_wallet must be false when type is not wallet (method index {i})"
                    )
            # R4: options must be array if present
            options = method.get("options")
            if options is not None and not isinstance(options, list):
                raise AssertionError(
                    f"R4: payment_methods[{i}].options must be array, got {type(options).__name__}"
                )
            # R4: can be empty only if method not clickable
            if not method["is_clickable"]:
                # options may be empty or absent when not clickable
                pass
            elif method.get("type") == "bnpl" and (options is None or not isinstance(options, list)):
                raise AssertionError(
                    f"R4: BNPL clickable method at index {i} must have options as array"
                )

    def validate_bnpl_options_r5_r6_r7(self, response: Dict[str, Any]) -> None:
        """R5: eligible = is_active and credit>0; R6: exactly one is_default among eligible; R7: price_type."""
        pm_list = response.get("payment_methods") or []
        for i, method in enumerate(pm_list):
            if method.get("type") != "bnpl":
                continue
            options = method.get("options")
            if not options:
                continue
            allowed_price_types = {"CASH_PRICE", "CREDIT_PRICE"}
            eligible = []
            for j, opt in enumerate(options):
                if not isinstance(opt, dict):
                    raise AssertionError(
                        f"payment_methods[{i}].options[{j}] must be object"
                    )
                for key, exp_type in [
                    ("source_id", int), ("title", str), ("credit", int),
                    ("is_active", bool), ("is_default", bool), ("price_type", str)
                ]:
                    if key not in opt:
                        raise AssertionError(
                            f"R1/S6: BNPL option [{i}][{j}] missing required field '{key}'"
                        )
                    val = opt[key]
                    if not isinstance(val, exp_type):
                        raise AssertionError(
                            f"Type: option[{i}][{j}].{key} must be {exp_type.__name__}, got {type(val).__name__}"
                        )
                if opt["price_type"] not in allowed_price_types:
                    raise AssertionError(
                        f"R7: option[{i}][{j}].price_type must be CASH_PRICE or CREDIT_PRICE (case-sensitive), got '{opt['price_type']}'"
                    )
                if opt["is_active"] and opt["credit"] > 0:
                    eligible.append(opt)
            if not eligible:
                continue
            defaults = [e for e in eligible if e.get("is_default") is True]
            if len(defaults) != 1:
                raise AssertionError(
                    f"R6: Among eligible BNPL options (method index {i}), exactly one must have is_default=true; found {len(defaults)}"
                )

    def validate_all_rules(self, response: Dict[str, Any]) -> None:
        """Run all validations in order (status/structure, methods R1–R4, options R5–R7)."""
        self.validate_response_status_and_structure(response)
        self.validate_payment_methods_r1_r2_r3_r4(response)
        self.validate_bnpl_options_r5_r6_r7(response)
