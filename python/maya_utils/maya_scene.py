class MayaBaseClass(object):
    CONST = (
        DEFAULT_ASSET_GEO_GROUP,
        DEFAULT_NO_REF_KEY,
        DEFAULT_CONSULADO_GEO_ATTR,
    ) = ("render_grp", "NO_REF", "cNodeId")

    def __init__(self):
        try:
            import maya.cmds as cmds
            import maya.mel as mel
            import pymel.core as pm
        except Exception as e:
            raise ImportError(
                "Error while importing the maya libraries, because: {}".format(e)
            )

        self.cmds = cmds
        self.mel = mel
        self.pm = pm


class MayaScene(MayaBaseClass):
    def __init__(self):
        super(MayaScene, self).__init__()
        self.cmds.namespace(setNamespace=":")
        self.no_intermediate_mesh_shapes = self.pm.ls(type="mesh", noIntermediate=True)
        self.scene_namespaces = (
            lambda: self.pm.namespaceInfo(listOnlyNamespaces=True, recurse=True) or []
        )
        self._assets = []

        self.load_assets()

    def __iter__(self):
        for asset in self._assets:
            if asset is None:
                continue
            yield asset

    def __len__(self):
        return len([i for i in self._assets if i is not None])

    def non_default_cameras(self):
        # Get all cameras first
        cameras = self.pm.ls(type=("camera"), l=True)

        # Let's filter all startup / default cameras
        startup_cameras = [
            camera
            for camera in cameras
            if self.pm.camera(camera.parent(0), startupCamera=True, q=True)
        ]

        non_default_cameras = list(set(cameras) - set(startup_cameras))

        for camera in map(lambda x: x.parent(0), non_default_cameras):
            yield camera

    def find_asset(self, namespace=None):
        if namespace:
            geometry_list = [
                m.getTransform()
                for m in self.no_intermediate_mesh_shapes
                if namespace in m.namespace()
                and self.DEFAULT_ASSET_GEO_GROUP in m.fullPath()
            ]
        else:
            geometry_list = [
                m.getTransform()
                for m in self.no_intermediate_mesh_shapes
                if self.DEFAULT_ASSET_GEO_GROUP in m.fullPath() and m.namespace() == ""
            ]
        if not geometry_list:
            return None

        return MayaAsset(geometry_list, namespace)

    def load_assets(self):
        self._assets.append(self.find_asset())
        for namespace in self.scene_namespaces():
            asset = self.find_asset(namespace)
            if asset is None:
                continue
            self._assets.append(asset)


class MayaAsset(MayaBaseClass):
    def __init__(self, geometry_list, namespace=None):
        super(MayaAsset, self).__init__()
        self._geometry_list = geometry_list
        self._namespace = (
            namespace if namespace is not None else self.DEFAULT_NO_REF_KEY
        )

    def __iter__(self):
        for geo in self._geometry_list:
            if geo is None:
                continue
            yield geo

    def __len__(self):
        return len([i for i in self._geometry_list if i is not None])

    @property
    def is_reference(self):
        return self._namespace != self.DEFAULT_NO_REF_KEY

    @property
    def namespace(self):
        if not self._geometry_list:
            return ""

        return "" if self._namespace == self.DEFAULT_NO_REF_KEY else self._namespace

    @property
    def node_ids(self):
        ids = []
        for geo in self._geometry_list:
            if not hasattr(geo, self.DEFAULT_CONSULADO_GEO_ATTR):
                continue

            attr = getattr(geo, self.DEFAULT_CONSULADO_GEO_ATTR)
            ids.append(attr.get())

        return ids

    @property
    def geos_without_sg_ids(self):
        return [
            geo
            for geo in self._geometry_list
            if not hasattr(geo, self.DEFAULT_CONSULADO_GEO_ATTR)
        ]

    def create_sg_attr(self):
        for geo in self.geos_without_sg_ids:
            self.pm.addAttr(geo, longName=self.DEFAULT_CONSULADO_GEO_ATTR, at="long")
