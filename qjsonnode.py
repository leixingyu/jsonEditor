"""
The node module is for creating node data structure/class that supports
hierarchical model. Each node object reflects to an abstract item which
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
        rootItem = cls(parent)
        rootItem.key = "root"
        rootItem.dtype = type(value)

        if isinstance(value, dict):
            # TODO: not sort will break things, but why?
            items = (
                sorted(value.items())
                if sort else value.items()
            )

            for key, value in items:
                child = cls.load(value, rootItem)
                child.key = key
                child.dtype = type(value)
                rootItem.addChild(child)
        elif isinstance(value, list):
            for index, value in enumerate(value):
                child = cls.load(value, rootItem)
                child.key = 'list[{}]'.format(index)
                child.dtype = type(value)
                rootItem.addChild(child)
        else:
            rootItem.value = value

        return rootItem

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

    def addChild(self, item):
        self._children.append(item)
        item._parent = self

    def removeChild(self, position):
        item = self._children.pop(position)
        item._parent = None

    def child(self, row):
        return self._children[row]

    def row(self):
        if self._parent:
            return self.parent.children.index(self)
        return 0

    def asJson(self):
        """
        Serialize to json
        """
        return {self.key: self.getChildrenValue(self)}

    def getChildrenValue(self, item):
        nchild = item.childCount

        if item.dtype is dict:
            document = dict()
            for i in range(nchild):
                ch = item.child(i)
                document[ch.key] = self.getChildrenValue(ch)
            return document
        elif item.dtype == list:
            document = list()
            for i in range(nchild):
                ch = item.child(i)
                document.append(self.getChildrenValue(ch))
            return document
        else:
            return item.value
