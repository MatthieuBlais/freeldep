class SNS:
    @classmethod
    def publish(cls, clients, topic, subject, message):
        clients.sns.publish(TopicArn=topic, Subject=subject, Message=message)
