import json
import paho.mqtt.client as mqtt

class ToDoListClient:
    def __init__(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to broker with result code " + str(rc))
        self.mqtt_client.subscribe("todo_list")

    def on_message(self, client, userdata, msg):
        payload = json.loads(msg.payload.decode())
        action = payload.get('action')

        if action == 'display':
            tasks = payload.get('tasks', [])
            self.display_todo_list(tasks)

    def display_todo_list(self, tasks):
        print("To-Do List:")
        for i, task_info in enumerate(tasks, start=1):
            print(f"{i}. Task: {task_info['task']}")
        print()

    def publish_task(self, task):
        payload = {'action': 'add', 'task': task}
        self.mqtt_client.publish("todo_list", json.dumps(payload))

    def run(self, broker_address, port=1883):
        self.mqtt_client.connect(broker_address, port, 60)
        self.mqtt_client.loop_start()

        try:
            while True:
                task = input("Enter task: ")
                self.publish_task(task)
        except KeyboardInterrupt:
            self.mqtt_client.disconnect()
            self.mqtt_client.loop_stop()

if __name__ == "__main__":
    todo_list_client = ToDoListClient()
    todo_list_client.run("127.0.0.1")  # Replace with your broker address
