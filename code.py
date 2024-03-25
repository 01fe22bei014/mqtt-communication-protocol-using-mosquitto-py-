import json
import time
import threading
import paho.mqtt.client as mqtt

class ToDoList:
    def __init__(self):
        self.tasks = []
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_message = self.on_message

    def connect_to_broker(self, broker_address, port=1883):
        self.mqtt_client.connect(broker_address, port, 60)
        self.mqtt_client.subscribe("todo_list")

    def on_message(self, client, userdata, msg):
        payload = json.loads(msg.payload.decode())
        action = payload.get('action')

        if action == 'add':
            self.add_task(payload['task'])
        elif action == 'update':
            self.update_task(payload['index'], payload['task'])
        elif action == 'delete':
            self.delete_task(payload['index'])

    def add_task(self, task):
        self.tasks.append({'task': task})
        self.print_todo_list()

    def update_task(self, index, task):
        if 0 <= index < len(self.tasks):
            self.tasks[index]['task'] = task
            self.print_todo_list()

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.print_todo_list()

    def print_todo_list(self):
        print("To-Do List:")
        for i, task_info in enumerate(self.tasks, start=1):
            print(f"{i}. Task: {task_info['task']}")
        print()

    def run(self):
        self.mqtt_client.loop_start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.mqtt_client.disconnect()
            self.mqtt_client.loop_stop()

if __name__ == "__main__":
    broker_address = "127.0.0.1"  # Update this with your broker address
    todo_list = ToDoList()
    todo_list.connect_to_broker(broker_address)

    # Start ToDoList thread
    todo_list_thread = threading.Thread(target=todo_list.run)
    todo_list_thread.start()

    try:
        while True:
            action = input("Enter action (add/update/delete/exit): ").lower()

            if action == 'exit':
                break
            elif action in ['add', 'update', 'delete']:
                index = int(input("Enter task index: "))
                task = input("Enter task description: ")

                payload = {
                    'action': action,
                    'index': index - 1,  # Adjust index to start from 0
                    'task': task,
                }
                todo_list.mqtt_client.publish("todo_list", json.dumps(payload))
            else:
                print("Invalid action. Try again.")
    except KeyboardInterrupt:
        pass
    finally:
        todo_list_thread.join()
