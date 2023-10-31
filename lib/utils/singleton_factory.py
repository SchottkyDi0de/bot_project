# Синглтон в питоне чаще всего не нужен: обычно хватает инициализировать один объект глобально
# в модуле и использовать его.
def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance
