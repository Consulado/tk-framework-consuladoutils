def get_custom_entity_by_alias(alias):
    """
    Get the real name of the Shotgun Custom Entity by alias.

    Args:
        alias(str): The shotgun custom entity alias name

    Returns:
        The custom entity name, otherwise, ``None`` if it alias doesn't exists.
    """
    return {
        "scene": "CustomEntity04",
        "node": "CustomEntity05",
        "node_type": "CustomNonProjectEntity01",
        "namespace": "CustomEntity03",
        "pre_production": "CustomEntity01",
    }.get(alias.lower())
