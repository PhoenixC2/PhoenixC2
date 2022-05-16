class Loader:
    """Loader Class to generate loaders"""
    def __init__(self, loader_type):
        self.loader_type = loader_type
    def create(self):
        raise NotImplementedError("Loader.create() not implemented")
    def obfuscate(self):
        raise NotImplementedError("Loader.obfuscate() not implemented")