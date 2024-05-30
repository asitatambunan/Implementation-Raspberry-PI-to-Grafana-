import RPi.GPIO as GPIO
import json
import time
from paho.mqtt import client as mqtt_client

broker = 'raspberrypi'
port = 1883
topic_publish = 'motion_detection_publish'
topic_subscribe = 'motion_detection_subscribe'
client_id = 'emqx'
username = 'user1'
password = 'user1'

pin_pir_sensor = 2  # GPIO pin for PIR sensor
pin_buzzer = 4  # GPIO pin for buzzer


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_pir_sensor, GPIO.IN)
GPIO.setup(pin_buzzer, GPIO.OUT)

def get_motion_status():
    if GPIO.input(pin_pir_sensor):
        return 1  # Motion detected
    else:
        return 0  # No motion detected

def control_buzzer(motion_status):
    if motion_status == 1:
        GPIO.output(pin_buzzer, GPIO.HIGH)
    else:
        GPIO.output(pin_buzzer, GPIO.LOW)

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n" % rc)
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish_motion_status(client, motion_status):
    msg = json.dumps({
        "motion_status": motion_status
    })
    result = client.publish(topic_publish, msg)
    status = result.rc
    if status == 0:
        print(f"Motion Status: {motion_status}, published to topic {topic_publish}")
    else:
        print(f"Failed to send message to topic {topic_publish}")

def on_message(client, userdata, msg):
    print(f"Received {str(msg.payload)} from topic {msg.topic}")

def publish_subscribe(client):
    client.on_message = on_message
    client.subscribe(topic_subscribe)
    while True:
        motion_status = get_motion_status()
        control_buzzer(motion_status)
        print(f"Motion Status: {motion_status}")
        publish_motion_status(client, motion_status)
        time.sleep(2)

def run():
    client = connect_mqtt()
    client.loop_start()
    publish_subscribe(client)

if __name__ == '__main__':
    run()
