"""Version information for Penguin Tamer."""

try:
    # Try to get version from setuptools_scm
    from importlib.metadata import version, PackageNotFoundError
    
    try:
        __version__ = version("penguin-tamer")
    except PackageNotFoundError:
        # Fallback if package not installed
        __version__ = "0.7.0.dev0"
        
except ImportError:
    # Fallback for older Python versions
    try:
        import pkg_resources
        __version__ = pkg_resources.get_distribution("penguin-tamer").version
    except Exception:
        __version__ = "0.7.0.dev0"