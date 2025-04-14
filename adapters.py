# Placeholder for future adapter implementations
class BaseAdapter:
    def __init__(self, resource: Dict):
        self.resource = resource

    async def connect(self):
        pass
