class EntityModel(object):
    def __init__(self, entity_type, fields, context, sg):
        self._entity_type = entity_type
        self._fields = fields
        self._filter = []

        self._context = context
        self._sg = sg

    @property
    def metadata(self):
        data = {}
        for (key, value) in self.__dict__.items():
            if key[0] == "_" or not value:
                continue

            value = value.shotgun_entity_data if isinstance(value, Entity) else value
            data[key] = value
        return data

    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, value):
        if isinstance(value, (list, tuple)):
            self._filter = value

    def load_data(self, *args, **kwargs):
        pass

    def put(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        pass


class Entity(EntityModel):
    def __init__(self, entity_type, fields, context, sg):
        super(Entity, self).__init__(entity_type, fields, context, sg)

        for f in fields:
            setattr(self, f, None)

        if "id" not in self._fields:
            self._fields += ["id"]
            setattr(self, "id", None)

        if "project" not in self._fields:
            self._fields += ["project"]
        setattr(self, "project", self._context.project)

    def load_data(self, filter_list=None):
        """
        Load the Shotgun data into this class

        Args:
            filter_list(list): The shotgun CRUD filter.
        """
        filter_list = filter_list if filter_list is not None else self.filter
        filter_list += [["project", "is", self._context.project]]
        data = self._sg.find_one(self._entity_type, filter_list, self._fields)
        if not data:
            # TODO: add logging warning
            return

        self.add_sg_data(data)

    def add_sg_data(self, data):
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

        return self.add_sg_data(
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

        return self.add_sg_data(self._sg.create(self._entity_type, data, return_fields))


class EntityIter(EntityModel):
    def __init__(self, entity_type, fields, context, sg):
        super(EntityIter, self).__init__(entity_type, fields, context, sg)

        self._entities = []

    def __iter__(self):
        for entity in self._entities:
            yield entity

    def __len__(self):
        return len(self._entities)

    def add_new_entity(self):
        entity = Entity(self._entity_type, self._fields, self._context, self._sg)
        self._entities.append(entity)
        return entity

    def remove_entity(self, entity_field, entity_value):
        removed_entity = None
        for entity in self._entities:
            attr = getattr(entity, entity_field)
            if attr == entity_value:
                removed_entity = entity
                self._entities.remove(entity)
                break
        if removed_entity:
            del removed_entity

    def load_data(self, filter_list=None):
        filter_list = filter_list if filter_list is not None else self.filter
        sg_data = self._sg.find(self._entity_type, filter_list, self._fields)

        if not sg_data:
            return

        new_entities = []
        for entity in sg_data:
            new_entity = Entity(
                self._entity_type, self._fields, self._context, self._sg
            )
            new_entity.add_sg_data(entity)
            new_entities.append(new_entity)

        self._entities = new_entities

    def put(self, multi_entity_update_modes=None):
        for entity in self._entities:
            entity.put(multi_entity_update_modes)

    def post(self, return_fields=None):
        for entity in self._entities:
            entity.post(return_fields)
