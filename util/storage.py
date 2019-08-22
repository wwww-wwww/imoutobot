import json

# basic json storage
class Storage:
    
    def __init__(self, path):
        self.path = path
        self.store = json.load(open("data/{}".format(path)))

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        if key in self.store:
            prev = self.store[key]
        self.store[key] = value

        if not self.save():
            if prev:
                self.store[key] = prev
            print("error saving")

    def __contains__(self, key):
        return key in self.store

    def keys(self):
        return self.store.keys()

    def length(self):
        return len(self.store)

    def set(self, key, value):
        self.store[key] = value
        return self.save()

    def append(self, value):
        self.store.append(value)
        return self.save()

    def remove(self, key):
        if type(self.store) is list:
            if key < len(self.store):
                del self.store[key]
                return self.save()
            return False
        if type(self.store) is dict:
            if key in self.store:
                del self.store[key]
                return self.save()
            return False

    def save(self):
        try:
            json.dump(self.store, open("data/{}".format(self.path), "w"))
            return True
        except IOError:
            return False
            