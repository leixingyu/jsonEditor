"""
The node module is for creating node data structure/class that supports
hierarchical model. Each node object reflects to an abstract node which
has child and parent relationships
"""


class QJsonNode(object):
    def __init__(self, parent=None):
        self._key = ""
        self._value = ""
        self._dtype = None
        self._parent = parent
        self._children = list()

    @classmethod
    def load(cls, value, parent=None, sort=1):
        rootNode = cls(parent)
        rootNode.key = "root"
        rootNode.dtype = type(value)

        if isinstance(value, dict):
            # TODO: not sort will break things, but why?
            nodes = (
                sorted(value.items())
                if sort else value.items()
            )

            for key, value in nodes:
                child = cls.load(value, rootNode)
                child.key = key
                child.dtype = type(value)
                rootNode.addChild(child)
        elif isinstance(value, list):
            for index, value in enumerate(value):
                child = cls.load(value, rootNode)
                child.key = 'list[{}]'.format(index)
                child.dtype = type(value)
                rootNode.addChild(child)
        else:
            rootNode.value = value

        return rootNode

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key):
        self._key = key

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def dtype(self):
        return self._dtype

    @dtype.setter
    def dtype(self, dtype):
        self._dtype = dtype

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return self._children

    @property
    def childCount(self):
        return len(self._children)

    def addChild(self, node):
        self._children.append(node)
        node._parent = self

    def removeChild(self, position):
        node = self._children.pop(position)
        node._parent = None

    def child(self, row):
        return self._children[row]

    def row(self):
        if self._parent:
            return self.parent.children.index(self)
        return 0

    def asDict(self):
        """
        Serialize to a dictionary
        """
        return {self.key: self.getChildrenValue(self)}

    def getChildrenValue(self, node):
        if node.dtype is dict:
            output = dict()
            for child in node.children:
                output[child.key] = self.getChildrenValue(child)
            return output
        elif node.dtype == list:
            output = list()
            for child in node.children:
                output.append(self.getChildrenValue(child))
            return output
        else:
            return node.value
