from xmlrpc.client import Boolean
from ...utils import Utilizator


class AnkiModulesValidator:
    """
    Klasa która waliduje dane z ANKI
    """
    def __init__(self, parent) -> None:
        self.parent = parent
        self.logger = self.parent.logger
        self.utilizator = Utilizator()
    
    def validateStructure(self, input_structure: list, dest_structure: dict) -> Boolean:
        """
        Funkcja do walidowania struktury modułów ANKI
        jeżeli struktura pól modelu jest poprawna, zwracany jest True
        jeżeli chociaż jedno pole nie nazwy się poprawnie, jest zwracany False
        """
        input_struct_processed = self.utilizator.utilizeWords(input_structure)
        dest_struct_processed = self.utilizator.utilizeWords(dest_structure.values())
        self.logger.info(f"Model words compare: in: {input_struct_processed} | dest: {dest_struct_processed}")
        return True if False not in list(map(lambda field: field in input_struct_processed, dest_struct_processed)) \
                    else False
