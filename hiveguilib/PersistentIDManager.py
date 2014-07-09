def id_generator():
    id_ = 0

    while True:
        yield id_
        id_ += 1


class PersistentIDManager:

    def __init__(self):
        self._id_generator = id_generator()

        self._persistent_to_temporary = {}
        self._temporary_to_persistent = {}

    def create_persistent_id(self, temporary_id):
        persistent_id = next(self._id_generator)

        self._persistent_to_temporary[persistent_id] = temporary_id
        self._temporary_to_persistent[temporary_id] = persistent_id

        return persistent_id

    def change_temporary_with_persistent_id(self, persistent_id, temporary_id):
        old_temporary = self._persistent_to_temporary[persistent_id]

        self._persistent_to_temporary[persistent_id] = temporary_id
        self._temporary_to_persistent[temporary_id] = persistent_id
        self._temporary_to_persistent.pop(old_temporary)

    def change_temporary_with_temporary_id(self, old_temporary, temporary_id):
        persistent_id = self._temporary_to_persistent.pop(old_temporary)

        self._persistent_to_temporary[persistent_id] = temporary_id
        self._temporary_to_persistent[temporary_id] = persistent_id

    def get_temporary_id(self, persistent_id):
        return self._persistent_to_temporary[persistent_id]

    def get_persistent_id(self, temporary_id):
        return self._temporary_to_persistent[temporary_id]

    def remove_with_persistent_id(self, persistent_id):
        temporary = self._persistent_to_temporary.pop(persistent_id)
        self._temporary_to_persistent.pop(temporary)

    def remove_with_temporary_id(self, temporary_id):
        persistent = self._temporary_to_persistent.pop(temporary_id)
        self._persistent_to_temporary.pop(persistent)
