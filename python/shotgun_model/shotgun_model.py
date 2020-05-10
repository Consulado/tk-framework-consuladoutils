class Entity(object):
    def __init__(self, entity_type, fields, context, sg):
        self._entity_type = entity_type
        self._fields = fields

        self._context = context
        self._sg = sg

        for f in fields:
            setattr(self, f, None)

        if "id" not in self._fields:
            self._fields += ["id"]
            setattr(self, "id", None)

        if "project" not in self._fields:
            self._fields += ["project"]
        setattr(self, "project", self._context.project)

    def load_data(self, filter_list):
        """
        Load the Shotgun data into this class

        Args:
            filter_list(list): The shotgun CRUD filter.
        """
        filter_list += [["project", "is", self._context.project]]
        data = self._sg.find_one(self._entity_type, filter_list, self._fields)
        if not data:
            # TODO: add logging warning
            return

        self._update_self(data)

    def _update_self(self, data):
        if isinstance(data, list):
            data = data[0]

        for key, value in data.items():
            setattr(self, key, value)
        return data

    @property
    def shotgun_entity_data(self):
        if not hasattr(self, "_entity_type") or not hasattr(self, "id"):
            raise AttributeError("This class doesn't have a valid id or type")
        return {"type": self._entity_type, "id": self.id}

    @property
    def metadata(self):
        data = {}
        for (key, value) in self.__dict__.items():
            if key[0] == "_" or not value:
                continue

            value = value.shotgun_entity_data if isinstance(value, Entity) else value
            data[key] = value
        return data

    def put(self, multi_entity_update_modes=None):
        data = self.metadata

        if not data:
            # TODO: logging this warning
            return {}

        entity_id = data.get("id")
        if entity_id:
            del data["id"]
        else:
            return {}

        return self._update_self(
            self._sg.update(
                self._entity_type, entity_id, data, multi_entity_update_modes
            )
        )

    def post(self, return_fields=None):
        data = self.metadata
        return_fields = return_fields or self._fields

        if not data:
            return {}

        if data.get("id"):
            del data["id"]

        return self._update_self(
            self._sg.create(self._entity_type, data, return_fields)
        )
