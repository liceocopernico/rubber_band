class Notifier:
    def __init__(self):
        self._subscribers = {}  

    def dispatch(self, events,screen):
        for event in events:
            subscribed = self._get_subscribers(event.type)
            for subscriber in subscribed:
                
                if callable(subscriber):
                    subscriber()
                elif isinstance(subscriber, object):
                    subscriber.handle_event(event,screen)

    def _get_subscribers(self, event_type):
        subscribers = self._subscribers.get(event_type)
        return subscribers if subscribers else []

    def subscribe(self, event, subscriber):
        """ Can be turned into a decorator but gets really complicated """
        subscribers = self._subscribers.get(event)
        if subscribers:
            subscribers.append(subscriber)
        else:
            self._subscribers.update({event: [subscriber]})

    def unsubscribe(self, event, subscriber):
        subscribers = self._get_subscribers(event)
        if subscribers:
            subscribers.remove(subscriber)