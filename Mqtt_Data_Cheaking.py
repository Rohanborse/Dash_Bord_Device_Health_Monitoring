import csv
import time
import logging
import paho.mqtt.client as mqtt
from datetime import datetime
import json  # Make sure json module is imported to parse the message
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Global variable to store received message
received_message = None


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        # logging.info("Connected to MQTT broker successfully")
        pass
    else:
        logging.error(f"Failed to connect to MQTT broker, return code {rc}")


def on_message(client, userdata, msg):
    global received_message
    logging.info(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
    received_message = msg.payload.decode()  # Store the received message globally
    userdata['received'] = True


def check_mqtt_data_for_all_rows(csv_file_path):
    not_receiving_data_machines = []
    try:
        with open(csv_file_path, mode="r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row_number, row in enumerate(csv_reader, start=1):
                try:
                    mqtt_broker = row['mqtt_broker'].strip()
                    mqtt_port = int(row['mqtt_port'])
                    mqtt_user = row['mqtt_user'].strip()
                    mqtt_pass = row['mqtt_pass'].strip()
                    topic = row['topic'].strip()
                    customer_name = row['Customer/Machine Name'].strip()

                    # Create MQTT client
                    userdata = {'received': False}
                    client = mqtt.Client(userdata=userdata)
                    client.username_pw_set(mqtt_user, mqtt_pass)
                    client.on_connect = on_connect
                    client.on_message = on_message

                    # Connect to the MQTT broker
                    client.connect(mqtt_broker, mqtt_port, 60)
                    client.subscribe(topic)

                    # Start the MQTT loop and wait for messages
                    client.loop_start()
                    start_time = time.time()
                    timeout = 60  # seconds
                    while not userdata['received'] and time.time() - start_time < timeout:
                        time.sleep(1)
                    client.loop_stop()

                    if userdata['received']:
                        # Process received message after the loop ends
                        if received_message:
                            try:
                                message_data = json.loads(received_message)
                                timestamp_str = message_data.get("datetime")
                                message_time = datetime.strptime(timestamp_str, '%d/%m/%Y %H:%M:%S')

                                current_time = datetime.now()
                                time_difference = current_time - message_time

                                if message_time.date() != current_time.date() or abs(
                                        time_difference.total_seconds()) > 7200:
                                    logging.warning(
                                        f"Data for {customer_name} on topic {topic} is outside the valid time window.")
                                    not_receiving_data_machines.append(customer_name)
                                else:
                                    logging.info(f"Data received successfully for {customer_name} on topic {topic}")
                            except Exception as e:
                                logging.error(f"Error parsing timestamp: {e}")
                                logging.warning(
                                    f"Data for {customer_name} on topic {topic} is outside the valid time window.")
                                not_receiving_data_machines.append(customer_name)
                    else:
                        logging.warning(
                            f"No data received for {customer_name} on topic {topic} within {timeout} seconds")
                        not_receiving_data_machines.append(customer_name)

                    # Disconnect the client
                    client.disconnect()

                except KeyError as e:
                    logging.error(f"Missing key in CSV row {row_number}: {e}")
                except Exception as e:
                    logging.error(f"Error processing row {row_number}: {e}")
    except FileNotFoundError:
        logging.error(f"CSV file {csv_file_path} not found")
    except Exception as e:
        logging.error(f"Error opening CSV file: {e}")

    for machine in not_receiving_data_machines:
        print(f"Machines not receiving data: {machine}", f"Last Data Recive on : {message_time}")

if __name__ == "__main__":
    csv_file_path = "Broker_CMD.csv"  # Update with your actual CSV file path
    check_mqtt_data_for_all_rows(csv_file_path)
