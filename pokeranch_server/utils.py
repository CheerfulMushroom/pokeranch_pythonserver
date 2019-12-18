def singleton(cls):
    """Simple wrapper for classes that should only have a single instance."""
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance
