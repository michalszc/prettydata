"""Protect documented imports, call signatures, annotations, and extension hooks."""

import importlib
import inspect
from typing import Any

import pytest

import tabloom
from tests.contracts.public_api.manifest import (
    FORWARDED_OPTIONS,
    PUBLIC_EXPORTS,
    PUBLIC_SIGNATURES,
)


def _resolve(endpoint: str) -> Any:
    """Resolve one root class or member using its supported top-level import."""
    name, _, member = endpoint.partition(".")
    owner = getattr(tabloom, name)
    return getattr(owner, member) if member else owner


@pytest.mark.parametrize("module_name", PUBLIC_EXPORTS)
def test_public_imports_retain_identity(module_name: str) -> None:
    """Root and component exports keep pointing to the same class objects."""
    module = importlib.import_module(module_name)
    expected = PUBLIC_EXPORTS[module_name]
    assert expected <= set(module.__all__)
    for name in expected:
        assert getattr(module, name) is getattr(tabloom, name)


@pytest.mark.parametrize("endpoint", PUBLIC_SIGNATURES)
def test_public_signatures_remain_compatible(endpoint: str) -> None:
    """Preserve defaults, parameter order/kinds, and accepted keyword forwarding."""
    parameters = inspect.signature(_resolve(endpoint)).parameters
    positional, keyword_only = PUBLIC_SIGNATURES[endpoint]
    for expected, kind in (
        (positional, inspect.Parameter.POSITIONAL_OR_KEYWORD),
        (keyword_only, inspect.Parameter.KEYWORD_ONLY),
    ):
        for name, default in expected.items():
            assert name in parameters, f"{endpoint} lost parameter {name}"
            assert parameters[name].default == default, f"{endpoint}.{name} default"
            assert parameters[name].kind is kind, f"{endpoint}.{name} kind"
    actual_order = [
        name
        for name, parameter in parameters.items()
        if name not in {"self", "cls"}
        and parameter.kind
        in {
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        }
    ]
    assert actual_order[: len(positional)] == list(positional), (
        f"{endpoint} positional order"
    )
    # Additive optional parameters remain valid; new required ones break callers.
    for name, parameter in parameters.items():
        if name not in {"self", "cls", *positional, *keyword_only}:
            assert (
                parameter.default is not inspect.Parameter.empty
                or parameter.kind
                in {
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                }
            ), f"{endpoint} added required parameter {name}"
    if endpoint in FORWARDED_OPTIONS:
        assert any(
            parameter.kind is inspect.Parameter.VAR_KEYWORD
            for parameter in parameters.values()
        ), f"{endpoint} no longer forwards matplotlib/pandas options"


@pytest.mark.parametrize("endpoint", PUBLIC_SIGNATURES)
def test_public_callables_remain_typed_and_documented(endpoint: str) -> None:
    """Public constructors and methods retain docstrings and type annotations."""
    value = _resolve(endpoint)
    assert inspect.getdoc(value), f"{endpoint} needs a public docstring"
    target = value.__init__ if inspect.isclass(value) else value
    signature = inspect.signature(target)
    assert signature.return_annotation is not inspect.Signature.empty, endpoint
    for name, parameter in signature.parameters.items():
        if name not in {"self", "cls"}:
            assert parameter.annotation is not inspect.Parameter.empty, (
                f"{endpoint}.{name} needs a type annotation"
            )
