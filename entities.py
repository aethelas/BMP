from abc import ABC, abstractmethod
import os


class BaseEntity(ABC):

    def __init__(self, name):
        self._name = str(name)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = str(value)

    @abstractmethod
    def get_info(self):
        raise NotImplementedError

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{type(self).__name__}(name={self.name!r})"

    def __eq__(self, other):
        if not isinstance(other, BaseEntity):
            return NotImplemented
        return type(self) is type(other) and self.name == other.name


class ImageInfo(BaseEntity):
    def __init__(self, path, width=0, height=0):
        self._path = ""
        self._width = 0
        self._height = 0
        super().__init__(os.path.basename(str(path)))
        self.path = path
        self.width = width
        self.height = height

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = str(value)
        self.name = os.path.basename(self._path)

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = max(0, int(value))

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = max(0, int(value))

    def get_info(self):
        return f"{self.width} x {self.height}"

    def __str__(self):
        return f"{self.name} ({self.get_info()})"

    def __repr__(self):
        return (
            f"ImageInfo(path={self.path!r}, "
            f"width={self.width!r}, height={self.height!r})"
        )

    def __eq__(self, other):
        if not isinstance(other, ImageInfo):
            return NotImplemented
        left = os.path.normcase(os.path.abspath(self.path))
        right = os.path.normcase(os.path.abspath(other.path))
        return left == right


class RecentFile(BaseEntity):
    def __init__(self, path):
        self._path = ""
        super().__init__(os.path.basename(str(path)))
        self.path = path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = str(value)
        self.name = os.path.basename(self._path)

    def get_info(self):
        return self.path

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"RecentFile(path={self.path!r})"

    def __eq__(self, other):
        if not isinstance(other, RecentFile):
            return NotImplemented
        left = os.path.normcase(os.path.abspath(self.path))
        right = os.path.normcase(os.path.abspath(other.path))
        return left == right


class KeyValueStore(BaseEntity):

    def __init__(self, items=None):
        self._items = []
        super().__init__("Настройки")
        if items is not None:
            for key, value in items:
                self.set(key, value)

    @property
    def items(self):
        return tuple(self._items)

    @items.setter
    def items(self, values):
        self._items = []
        for key, value in values:
            self.set(key, value)

    def get_info(self):
        return f"Хранится настроек: {len(self)}"

    def set(self, key, value):
        for index, (saved_key, _) in enumerate(self._items):
            if saved_key == key:
                self._items[index] = (key, value)
                return
        self._items.append((key, value))

    def get(self, key, default=None):
        for saved_key, value in self._items:
            if saved_key == key:
                return value
        return default

    def remove(self, key):
        for index, (saved_key, _) in enumerate(self._items):
            if saved_key == key:
                del self._items[index]
                return True
        return False

    def __len__(self):
        return len(self._items)

    def __contains__(self, key):
        return any(saved_key == key for saved_key, _ in self._items)

    def __iter__(self):
        return iter(tuple(self._items))

    def __str__(self):
        return f"Настроек: {len(self)}"

    def __repr__(self):
        return f"KeyValueStore(items={self._items!r})"

    def __eq__(self, other):
        if not isinstance(other, KeyValueStore):
            return NotImplemented
        return self._items == other._items
