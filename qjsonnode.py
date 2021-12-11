"""
The node module is for creating node data structure/class that supports
hierarchical model. Each node object reflects to an abstract node which
has child and parent relationships
"""


class QJsonNode(object):
    def __init__(self, parent=None):
        """
        Initialization

        :param parent: QJsonNode. parent of the current node
        """
        self._key = ""
        self._value = ""
        self._dtype = None
        self._parent = parent
        self._children = list()

    @classmethod
    def load(cls, value, parent=None):
        """
        Generate the hierarchical node tree using dictionary

        :param value: dict. input dictionary
        :param parent: QJsonNode. for recursive use only
        :return: QJsonNode. the top node
        """
        rootNode = cls(parent)
        rootNode.key = "root"
        rootNode.dtype = type(value)

        if isinstance(value, dict):
            # TODO: not sort will break things, but why?
            nodes = sorted(value.items())

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
        """
        Get key of the current node
        """
        return self._key

    @key.setter
    def key(self, key):
        self._key = key

    @property
    def value(self):
        """
        Get value of the current node
        """
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def dtype(self):
        """
        Get value data type of the current node
        """
        return self._dtype

    @dtype.setter
    def dtype(self, dtype):
        self._dtype = dtype

    @property
    def parent(self):
        """
        Get parent node of the current node
        """
        return self._parent

    @property
    def children(self):
        """
        Get the children of the current node
        :return: list.
        """
        return self._children

    @property
    def childCount(self):
        """
        Get the number of children of the current node
        :return: int.
        """
        return len(self._children)

    def addChild(self, node):
        """
        Add a new child to the current node

        :param node: QJsonNode. child node
        """
        self._children.append(node)
        node._parent = self

    def removeChild(self, position):
        """
        Remove child on row/position of the current node

        :param position: int. index of the children
        """
        node = self._children.pop(position)
        node._parent = None

    def child(self, row):
        """
        Get the child on row/position of the current node

        :param row: int. index of the children
        :return: QJsonNode. child node
        """
        return self._children[row]

    def row(self):
        """
        Get the current node's row/position in regards to its parent

        :return: int. index of the current node
        """
        if self._parent:
            return self.parent.children.index(self)
        return 0

    def asDict(self):
        """
        Serialize the hierarchical structure of current node to a dictionary

        :return: dict. serialization of the hierarchy
        """
        return {self.key: self.getChildrenValue(self)}

    def getChildrenValue(self, node):
        """
        Query the nested children value (instead of a single value)

        :param node: QJsonNode. root node
        :return: mixed. value
        """
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
