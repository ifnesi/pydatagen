# Python emulator of the Kafka source connector Datagen

## Requirements:
- Python 3.8+
- see requirements.txt

## Important:
 - Folder "resources/" was forked on 19-Nov-2022 (from https://github.com/confluentinc/kafka-connect-datagen/tree/master/src/main/resources)
 - In case "arg.properties" is not defined in the schema file, a random value will be picked (int/long: 1 to 9999, double: 0.00 to 99.99, boolean: true or false, string: 4 to 8 random alphanumeric chars)
 - Schema will be cleaned up of "arg.properties" before sending to the Schema Registry

## Usage and help
<pre>
usage: <span style="color:green">
  pydatagen.py [-h] --schema-filename SCHEMA_FILENAME [--keyfield KEYFIELD] [--key-json] --topic TOPIC [--set-headers] [--dry-run] [--bootstrap-servers BOOTSTRAP_SERVERS]
               [--schema-registry SCHEMA_REGISTRY] [--iterations ITERATIONS] [--interval INTERVAL] [--silent]
</span>
options:<span style="color:green">
  -h, --help            show this help message and exit
  --schema-filename SCHEMA_FILENAME
                        Avro schema file name
  --keyfield KEYFIELD   Name of the field to be used as message key
  --key-json            Set key as JSON -> {{keyfield: keyfield_value}}
  --topic TOPIC         Topic name
  --set-headers         Set headers with lineage data
  --dry-run             Generate and display messages without having them publish
  --bootstrap-servers BOOTSTRAP_SERVERS
                        Bootstrap broker(s) (host[:port])
  --schema-registry SCHEMA_REGISTRY
                        Schema Registry (http(s)://host[:port]
  --iterations ITERATIONS
                        Number of messages to be sent
  --interval INTERVAL   Max interval between messages (in milliseconds)
  --silent              Do not display results on screen (not applicable in dry run mode)
  </span>
<span style="color:red">Pending auth to Confluent Cloud (SASL_SSL)</span>
</pre>

## Examples:
### Input (dry run mode)
<pre style="color:green">
python3 pydatagen.py --schema-filename gaming_players.avro --dry-run --set-headers --keyfield player_id --key-json --interval 1000 --iterations 10
</pre>
### Output (dry run mode)
<pre style="color:grey">
Producing 10 messages in dry run mode. ^C to exit.

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
python3 pydatagen.py --schema-filename gaming_players.avro --set-headers --keyfield player_id --key-json --interval 1000 --iterations 10 --topic test2
</pre>
### Output
<pre style="color:grey">
Producing 10 messages to topic 'test2'. ^C to exit.

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