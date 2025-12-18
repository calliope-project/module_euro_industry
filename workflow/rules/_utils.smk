"""Collection of auxiliary functions for this module."""


def get_ghsl_url(epoch: int, resolution: int) -> str:
    """Ensures technology mapping and lifetime-related names match."""
    return internal["resources"]["automatic"]["GHSL"].format(
        epoch=epoch, resolution=resolution
    )
