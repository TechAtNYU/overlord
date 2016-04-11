class Event(object):

    """
    Class to represent a Tech @ NYU Event
    """

    def __init__(self, json_obj):
        self.id = json_obj['id']
        self._attributes = json_obj['attributes']

    def __getattr__(self, attr):
        if attr not in self._attributes:
            raise AttributeError("Event object has no attribute " + attr)
        return self._attributes[attr]

    def __repr__(self):
        return self.title.encode('utf-8')
