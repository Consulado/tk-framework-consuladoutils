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
    def entity_filter(self):
        return self._filter

    @entity_filter.setter
    def entity_filter(self, value):
        if isinstance(value, (list, tuple)):
            self._filter = value

    def load(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass

    def create(self, *args, **kwargs):
        pass


class Entity(EntityModel):
    """
    This class encapsulates the Shotgun Entity data and give the Shotgun CRUD methods as well
    """

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

    @property
    def shotgun_entity_data(self):
        """
        This property parametrize the return of this class like the Shotgun entity return

        Returns:
            Returns a dict with the entity type and entity id

        Raises
            AttributeError: When this class haven't type or id.
        """
        if not hasattr(self, "_entity_type") or not hasattr(self, "id"):
            raise AttributeError("This class doesn't have a valid id or type")
        return {"type": self._entity_type, "id": self.id}

    def add_sg_data(self, data):
        if isinstance(data, list):
            data = data[0]

        for key, value in data.items():
            setattr(self, key, value)
        return data

    def load(self, entity_filter=None):
        """
        Load the Shotgun data into this class

        Args:
            entity_filter(list): The Shotgun CRUD filter.
        """
        entity_filter = (
            entity_filter if entity_filter is not None else self.entity_filter
        )
        entity_filter += [["project", "is", self._context.project]]
        data = self._sg.find_one(self._entity_type, entity_filter, self._fields)
        if not data:
            # TODO: add logging warning
            return

        self.add_sg_data(data)

    def update(self, multi_entity_update_modes=None):
        """
        Commit changes on Shotgun.
        Args:
            multi_entity_update_modes(dict): Optional dict indicating what update mode to use when updating a
                multi-entity link field. The keys in the dict are the fields to set the mode for, and the values
                from the dict are one of ``set``, ``add``, or ``remove``. Defaults to ``set``.
        Returns:
            Dictionary of the fields updated
        """
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

    def create(self, return_fields=None):
        """
        Create a new entity with the specified ``type``
        Args:
            return_fields(list): optional argument. When this argument is ``None``, this method considers only the `` fields`` provided in the constructor of that class.

        Returns:
            Shotgun entity dictionary containing the field/value pairs of all of the fields set from the data parameter
            as well as the defaults type and id. If any additional fields were provided using the return_fields parameter,
            these would be included as well.
        """
        data = self.metadata
        return_fields = return_fields or self._fields

        if not data:
            return {}

        if data.get("id"):
            del data["id"]

        return self.add_sg_data(self._sg.create(self._entity_type, data, return_fields))


class EntityIter(EntityModel):
    """
    This class interacts with the many Shotgun Entity data and give the Shotgun CRUD methods as well.

    This class allows the for/loop and len method to access the surveyed entities' data.
    """

    def __init__(self, entity_type, fields, context, sg):
        super(EntityIter, self).__init__(entity_type, fields, context, sg)

        self._entities = []

    def __iter__(self):
        for entity in self._entities:
            yield entity

    def __len__(self):
        return len(self._entities)

    def add_new_entity(self):
        """
        Add new entity with the same type and return it. This method will not commit automatically this data on Shotgun.

        Returns:
            (Entity): The ``Entity`` class instance
        """
        entity = Entity(self._entity_type, self._fields, self._context, self._sg)
        self._entities.append(entity)
        return entity

    def remove_entity(self, entity_field, entity_value):
        """
        It removes the entity found by ``entity_field`` and ``entity_value`` from the entities internal list and it deletes this class instance.

        Args:
            entity_field(str): The entity field name
            entity_value(str): The entity field value
        """
        removed_entity = None
        for entity in self._entities:
            attr = getattr(entity, entity_field)
            if attr == entity_value:
                removed_entity = entity
                self._entities.remove(entity)
                break
        if removed_entity:
            del removed_entity

    def load(self, entity_filter=None):
        """
        Find all Shotgun entities and creates a new ``Entity`` class instances with the Shotgun data encapsulated
        Args:
            entity_filter(list): The Shotgun CRUD filter.
                For example::
                    entity_filter=[["project", "is", {"type": "Project", "id": 123}], ["code", "is", "some_code"]]
        """
        entity_filter = (
            entity_filter if entity_filter is not None else self.entity_filter
        )
        sg_data = self._sg.find(self._entity_type, entity_filter, self._fields)

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

    def update(self, multi_entity_update_modes=None):
        """
        Commit changes on Shotgun.
        Args:
            multi_entity_update_modes(dict): Optional dict indicating what update mode to use when updating a
                multi-entity link field. The keys in the dict are the fields to set the mode for, and the values
                from the dict are one of ``set``, ``add``, or ``remove``. Defaults to ``set``.
        """
        for entity in self._entities:
            entity.update(multi_entity_update_modes)

    def create(self, return_fields=None):
        """
        Create a new entity with the specified ``type``
        Args:
            return_fields(list): optional argument. When this argument is ``None``, this method considers only the `` fields`` provided in the constructor of that class.
        """
        for entity in self._entities:
            entity.create(return_fields)
