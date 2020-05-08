class Edge:
    def __init__(self, target, event, fromGraph, toGraph):
        self.target = target
        self.event = event
        self.fromGraph = fromGraph
        self.toGraph = toGraph

    def toJson(self):
        res = {}
        res["fromGraph"] = self.fromGraph
        res["toGrapph"] = self.toGraph
        res["target"] = self.target
        res["event"] = self.event

        return res

