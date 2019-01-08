import plyvel
from iconservice.base.address import Address, AddressPrefix


class ScoreDatabaseManager(object):
    def __init__(self):
        self._db = None
        self._score_address = None

    def open(self, db_path: str, score_address: 'Address'):
        self._db = plyvel.DB(db_path, create_if_missing=False)
        self._score_address: 'Address' = score_address

    def read_from_dict_db(self, dict_db_name: str, address: 'Address') -> bytes:
        key: bytes = self._create_dict_db_key(dict_db_name, address)
        return self._db.get(key)

    def write_to_dict_db(self, dict_db_name: str, address: 'Address', value: bytes):
        key: bytes = self._create_dict_db_key(dict_db_name, address)
        self._db.put(key, value)

    def _create_dict_db_key(self, dict_db_name: str, address: bytes) -> bytes:
        dict_db_data_type: bytes = b'\x01'
        items = [
            self._score_address.to_bytes(),
            dict_db_data_type,
            dict_db_name.encode('utf-8'),
            address]

        return b'|'.join(items)

    def close(self):
        if self._db is None:
            return

        self._db.close()
        self._db = None
        self._score_address = None
