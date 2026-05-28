import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from shared.messaging.base_publisher import BasePublisher

class ReviewSubmittedPublisher(BasePublisher):
    def __init__(self):
        super().__init__("ReviewSubmittedEvent")
