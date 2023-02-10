# Python emulator of the Kafka source connector Datagen

## Requirements:
- Python 3.8+
- See file requirements.txt (python3 -m pip install -r requirements.txt)

## Important:
 - This is a Kafka Producer and it does not use the Kafka Connect framework, also it is a single worker producer and "acks" is set to 0 (meaning, it will not wait for any acknowledgement from the broker)
 - The purpose of it is not to replace the Datagen source connector (far from that), but instead to be used for demo/development when setting up a dummy-data producer where the data produced (message, headers and key) can be seen on the console and in the corresponding topic in the kafka cluster. It has an argument called “--dry-run” to display messages in the console instead of publishing to the Kafka cluster
 - Folder "resources/" was forked on 19-Nov-2022 (from https://github.com/confluentinc/kafka-connect-datagen/tree/master/src/main/resources)
 - In case "arg.properties" is not defined in the schema file, a random value will be picked (int/long: 1 to 9999, double: 0.00 to 99.99, boolean: true or false, string: 4 to 8 random alphanumeric chars)
 - Schema will be cleaned up of "arg.properties" before sending to the Schema Registry
 - Message headers can be set dynamically (python script, make sure to set a global variable called "headers") or statically (json file). All header files must be inside the folder "headers/"

## To do:
 - Support to JSON, JSON_SR and PROTOBUF schemas

## Usage and help
<pre>
usage: <span style="color:green">
  pydatagen.py [-h] [--client-id CLIENT_ID] 
               --schema-filename SCHEMA_FILENAME
               --topic TOPIC [--headers-filename HEADERS_FILENAME] [--dry-run]
               [--keyfield KEYFIELD] [--key-json]
               [--bootstrap-servers BOOTSTRAP_SERVERS]
               [--schema-registry SCHEMA_REGISTRY]
               [--iterations ITERATIONS]
               [--interval INTERVAL]
               [--config-filename CONFIG_FILENAME]
               [--kafka-section KAFKA_SECTION]
               [--sr-section SR_SECTION]
               [--silent]
</span>
options:<span style="color:green">
  -h, --help            show this help message and exit
  --client-id CLIENT_ID
                        Producer's Client ID (if not set the default is pydatagen_XXXXXXXX, where XXXXXXXX is a unique id based on topic and schema
                        filename)

  --schema-filename SCHEMA_FILENAME
                        Avro schema file name (files must be inside the folder resources/)

  --keyfield KEYFIELD   Name of the field to be used as message key (required if argument --key-json is set)

  --key-json            Set key as JSON -> {{keyfield: keyfield_value}}

  --topic TOPIC         Topic name (required if argument --dry-run is not set)

  --headers-filename HEADERS_FILENAME
                        Select headers filename (files must be inside the folder headers/)

  --dry-run             Generate and display messages without having them publish

  --bootstrap-servers BOOTSTRAP_SERVERS
                        Bootstrap broker(s) (host[:port])

  --schema-registry SCHEMA_REGISTRY
                        Schema Registry (http(s)://host[:port])

  --iterations ITERATIONS
                        Number of messages to be sent (default: 9999999999999)

  --interval INTERVAL   Max interval between messages in milliseconds (default: 500))

  --config-filename CONFIG_FILENAME
                        Select config filename for additional configuration, such as credentials (files must be inside the folder config/)

  --kafka-section KAFKA_SECTION
                        Section in the config file related to the Kafka cluster (e.g. kafka)

  --sr-section SR_SECTION
                        Section in the config file related to the Schema Registry (e.g. schema-registry)

  --silent              Do not display results on screen (not applicable to dry-run mode)
  </span>
</pre>

## Examples:
### Input (dry-run mode)
<pre style="color:green">
python3 pydatagen.py --schema-filename gaming_players.avro --dry-run \
                     --headers-filename dynamic_000.py --keyfield player_id \
                     --key-json --interval 1000 --iterations 10
</pre>
### Output (dry-run mode)
<pre style="color:grey">
Producing 10 messages in dry-run mode. ^C to exit.

message #1: {'player_id': 1072, 'player_name': 'Talbot Cashell', 'ip': '104.16.237.57'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1072}

message #2: {'player_id': 1053, 'player_name': 'Cirstoforo Joblin', 'ip': '37.136.192.70'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1053}

message #3: {'player_id': 1047, 'player_name': 'Cort Bainbridge', 'ip': '26.45.199.135'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1047}

message #4: {'player_id': 1041, 'player_name': 'Fitz Ballin', 'ip': '61.160.45.31'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1041}

message #5: {'player_id': 1092, 'player_name': 'Faye Beaument', 'ip': '77.208.184.143'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1092}

message #6: {'player_id': 1034, 'player_name': 'Jori Ottiwill', 'ip': '44.125.117.30'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1034}

message #7: {'player_id': 1009, 'player_name': 'Winny Cadigan', 'ip': '68.145.84.22'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1009}

message #8: {'player_id': 1059, 'player_name': 'Riva Rossant', 'ip': '64.39.185.31'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1059}

message #9: {'player_id': 1051, 'player_name': 'Nathaniel Hallowell', 'ip': '206.228.92.173'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1051}

message #10: {'player_id': 1095, 'player_name': 'Chryste Wren', 'ip': '141.46.127.99'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1095}
</pre>

### Input
<pre style="color:green">
python3 pydatagen.py --schema-filename gaming_players.avro \
                     --headers-filename dynamic_000.py --keyfield player_id \
                     --key-json --interval 1000 --iterations 10 --topic test2
</pre>
### Output
<pre style="color:grey">
Producing 10 messages to topic 'test2' via client.id 'pydatagen_a7cc48eb'. ^C to exit.

message #1: {'player_id': 1079, 'player_name': 'Nertie Zuker', 'ip': '219.151.0.93'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1079}
> Message successfully produced to test2: Partition = 0, Offset = 391

message #2: {'player_id': 1020, 'player_name': 'Pattin Eringey', 'ip': '66.106.114.58'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1020}
> Message successfully produced to test2: Partition = 0, Offset = 392

message #3: {'player_id': 1006, 'player_name': 'Brenna Woolfall', 'ip': '46.152.206.98'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1006}
> Message successfully produced to test2: Partition = 0, Offset = 393

message #4: {'player_id': 1053, 'player_name': 'Cirstoforo Joblin', 'ip': '37.136.192.70'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1053}
> Message successfully produced to test2: Partition = 0, Offset = 394

message #5: {'player_id': 1099, 'player_name': 'Raychel Roset', 'ip': '183.237.217.217'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1099}
> Message successfully produced to test2: Partition = 0, Offset = 395

message #6: {'player_id': 1062, 'player_name': 'Aryn Haskell', 'ip': '215.235.104.14'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1062}
> Message successfully produced to test2: Partition = 0, Offset = 396

message #7: {'player_id': 1006, 'player_name': 'Brenna Woolfall', 'ip': '46.152.206.98'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1006}
> Message successfully produced to test2: Partition = 0, Offset = 397

message #8: {'player_id': 1058, 'player_name': 'Aldrich MacVay', 'ip': '198.1.226.227'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1058}
> Message successfully produced to test2: Partition = 0, Offset = 398

message #9: {'player_id': 1036, 'player_name': 'Zechariah Wrate', 'ip': '11.107.127.127'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1036}
> Message successfully produced to test2: Partition = 0, Offset = 399

message #10: {'player_id': 1100, 'player_name': 'Heindrick Ravenscroft', 'ip': '165.19.12.241'}
headers: {'program': 'python', 'version': '3.10.8', 'node': 'P3W32CDKHC', 'environment': 'test'}
key: {"player_id": 1100}

Flushing messages...
> Message successfully produced to test2: Partition = 0, Offset = 400
</pre>