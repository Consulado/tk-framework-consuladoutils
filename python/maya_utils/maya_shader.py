import os
import random
import string


class BaseShader(object):
    def __init__(self):
        import pymel.core as pm
        import maya.cmds as cmds

        self.pm = pm
        self.cmds = cmds

    @property
    def shader(self):
        raise NotImplementedError()

    @property
    def nodes(self):
        raise NotImplementedError()

    @shader.setter
    def shader(self, value):
        raise NotImplementedError()

    @nodes.setter
    def nodes(self, value):
        raise NotImplementedError()

    def fetch(self):
        raise NotImplementedError()

    def apply(self):
        raise NotImplementedError()


class ShaderIter(BaseShader):
    def __init__(self, nodes=None, local_data=None):
        if not isinstance(nodes, (list, tuple)):
            nodes = [nodes]

        self._nodes = nodes
        self._shader = []
        self.local_data = local_data
        super(ShaderIter, self).__init__()

    def __iter__(self):
        for shader in self._shader:
            yield shader

    def __len__(self):
        return len(self._shader)

    def __enter__(self):
        self.fetch()
        return self

    def __exit__(self, *args, **kwargs):
        pass

    @property
    def nodes(self):
        return self._nodes

    @nodes.setter
    def nodes(self, value):
        if not isinstance(value, (list, tuple)):
            value = [value]
        self._nodes = value

    @property
    def shader(self):
        return self._shader

    @staticmethod
    def _get_random_string(length):
        letters = string.ascii_lowercase
        return "".join(random.choice(letters) for i in range(length))

    def fetch(self):
        shaders = []
        temp_shader_data = {}
        if self.local_data is None:
            for node in self.nodes:
                node = self.pm.PyNode(node)
                if node.nodeType() == "transform":
                    node = node.getShape()
                shading_eng = node.listConnections(type="shadingEngine")
                if shading_eng:
                    shading_eng_name = shading_eng[0].nodeName()
                    if temp_shader_data.get(shading_eng_name):
                        temp_shader_data[shading_eng_name] += [node]
                    else:
                        temp_shader_data[shading_eng_name] = [node]
        else:
            for path, nodes in self.local_data.items():
                # creating file reference with shaders and materials
                file_reference = self.pm.createReference(
                    path, namespace=self._get_random_string(12)
                )
                # get shadingEngine object
                shading_eng = [
                    s for s in file_reference.nodes() if s.nodeType() == "shadingEngine"
                ]
                file_reference.importContents(removeNamespace=True)
                if shading_eng:
                    shading_eng_name = shading_eng[0].nodeName()
                    temp_shader_data[shading_eng_name] = [nodes]

        if temp_shader_data:
            for shading_eng_name, nodes in temp_shader_data.items():
                shader = Shader(nodes)
                shader.shading_engine = shading_eng_name
                shader.fetch()
                shaders.append(shader)

            self._shader = shaders

    def apply(self):
        for shader in self.shader:
            try:
                shader.apply()
            except Exception as e:
                print(
                    "Problems to apply the shader {}, the system returns: {}".format(
                        shader, e
                    )
                )
                continue


class Shader(BaseShader):
    def __init__(self, nodes):
        if not isinstance(nodes, (list, tuple)):
            nodes = [nodes]

        self._nodes = nodes
        self._shader = []
        self._shading_engine = None
        super(Shader, self).__init__()

    def __iter__(self):
        for shader in self._shader:
            yield shader

    def __len__(self):
        return len(self._shader)

    @property
    def shading_engine(self):
        return self._shading_engine

    @shading_engine.setter
    def shading_engine(self, value):
        n = self.pm.PyNode(value)
        if n.nodeType() != "shadingEngine":
            raise RuntimeError("This property must need to shadingEngine node type")

        self._shading_engine = n

    @property
    def nodes(self):
        return self._nodes

    @nodes.setter
    def nodes(self, value):
        if not isinstance(value, (list, tuple)):
            value = [value]
        self._nodes = value

    @property
    def shader(self):
        return self._shader

    @staticmethod
    def _list_all_shader_nodes(node):
        conn = node.listConnections(destination=False, source=True)
        all_nodes = [node]
        if not conn:
            return all_nodes
        else:
            for c in conn:
                all_nodes += Shader._list_all_shader_nodes(c)
            return list(
                set([n for n in all_nodes if n.nodeType() not in ["transform"]])
            )

    def fetch(self):
        if self.shading_engine is None:
            return

        self._shader = self._list_all_shader_nodes(self.shading_engine)

    def apply(self):
        self.pm.sets(self.shading_engine, edit=True, forceElement=self.nodes)

    def export(self, path):
        self.cmds.select(self.shader, replace=True, noExpand=True)
        self.cmds.file(
            path, type="mayaAscii", exportSelected=True, shader=True, force=True
        )

        if os.path.isfile(path):
            return True
        else:
            return False
