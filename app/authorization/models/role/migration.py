"""
Custom permission creation system.

This module overrides Django's default permission creation to support:
1. `CREATE_DEFAULT_PERMISSIONS = True` as model class attribute for CRUD permissions
2. Custom permission format: "app_label.model_name.action" as codename
3. JSON-formatted names for multi-language support

Usage in models:
    class Camera(BaseModel):
        CREATE_DEFAULT_PERMISSIONS = True  # Enable CRUD permissions

        class Meta:
            permissions = [
                ("assets.camera.get_snapshot", '{"en": "Get Snapshot From Camera", "tr": "Kameradan Anlık Görüntü Al"}'),
            ]

Permission codename format: app_label.model_name.action
Examples:
    - assets.camera.view
    - assets.camera.add
"""

import json

from django.apps import apps as global_apps
from django.db import DEFAULT_DB_ALIAS

# Default CRUD actions
DEFAULT_ACTIONS = ("view", "add", "change", "delete")

# Default action names in multiple languages
DEFAULT_ACTION_NAMES = {
    "view": {"en": "View", "tr": "Görüntüle"},
    "add": {"en": "Add", "tr": "Ekle"},
    "change": {"en": "Change", "tr": "Değiştir"},
    "delete": {"en": "Delete", "tr": "Sil"},
}


def get_permission_codename(app_label: str, model_name: str, action: str) -> str:
    """Generate permission codename in format 'app_label.model_name.action'."""
    return f"{app_label}.{model_name}.{action}"


def get_permission_name(action: str, model_verbose_name: str) -> dict:
    """
    Generate permission name as dict with multi-language support.

    Returns dict like: {"en": "View Camera", "tr": "Kamera Görüntüle"}
    """
    action_names = DEFAULT_ACTION_NAMES.get(action, {"en": action.title(), "tr": action.title()})
    return {
        "en": f"{action_names['en']} {model_verbose_name}",
        "tr": f"{model_verbose_name} {action_names['tr']}",
    }


def get_model_permissions(model):
    """
    Get all permissions for a model.

    Returns list of (codename, name_dict) tuples.
    """
    opts = model._meta
    app_label = opts.app_label
    model_name = opts.model_name
    verbose_name = str(opts.verbose_name).title()

    perms = []

    # Check if model wants default CRUD permissions (class attribute)
    create_defaults = getattr(model, "CREATE_DEFAULT_PERMISSIONS", False)
    if create_defaults:
        for action in DEFAULT_ACTIONS:
            codename = get_permission_codename(app_label, model_name, action)
            name = get_permission_name(action, verbose_name)
            perms.append((codename, name))

    # Add custom permissions from Meta.permissions
    for perm in opts.permissions:
        codename, name = perm[0], perm[1]
        # If name is a JSON string, parse it
        if isinstance(name, str):
            try:
                name = json.loads(name)
            except json.JSONDecodeError:
                name = {"en": name, "tr": name}
        perms.append((codename, name))

    return perms


def create_permissions(
    sender,
    verbosity=2,
    interactive=True,
    using=DEFAULT_DB_ALIAS,
    apps=global_apps,
    **kwargs,
):
    """
    Create permissions for all models in the given app.

    This function replaces Django's default create_permissions to support
    our custom Permission model with CREATE_DEFAULT_PERMISSIONS flag.

    Called via post_migrate signal for each app.
    """
    app_config = sender

    if not app_config.models_module:
        return

    # Use our custom Permission model
    try:
        Permission = apps.get_model("authorization", "Permission")
    except LookupError:
        return

    # Check if Permission table exists
    if not Permission._meta.db_table:
        return

    models = list(app_config.get_models())

    # Get existing permission codenames
    existing_codenames = set(Permission.objects.using(using).values_list("codename", flat=True))

    perms_to_create = []
    for model in models:
        # Get permissions for this model (respects CREATE_DEFAULT_PERMISSIONS)
        for codename, name in get_model_permissions(model):
            if codename not in existing_codenames:
                permission = Permission(
                    codename=codename,
                    name=name,
                )
                permission._state.db = using
                perms_to_create.append(permission)
                existing_codenames.add(codename)  # Prevent duplicates in same batch

    if perms_to_create:
        Permission.objects.using(using).bulk_create(perms_to_create)

        if verbosity >= 2:
            for perm in perms_to_create:
                print(f"Adding permission '{perm.codename}'")
