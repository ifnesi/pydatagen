# -*- coding: utf-8 -*-
#
# Copyright 2022 Confluent Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Generic Avro consumer, message will be deserialised as per AVRO schema set on each event

import os
import logging
import argparse

from configparser import ConfigParser
from confluent_kafka import Consumer, KafkaException
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

# Global Variables
FILE_APP = os.path.split(__file__)[-1]
FOLDER_APP = os.path.dirname(__file__)
FOLDER_CONFIG = "config"

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d [%(levelname)s]: %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main(args):
    kconfig = ConfigParser()
    kconfig.read(os.path.join(FOLDER_CONFIG, args.config_filename))

    # Configure Kafka consumer
    conf_confluent = {
        "bootstrap.servers": args.bootstrap_servers,
        "group.id": args.group_id,
        "client.id": args.client_id,
        "auto.offset.reset": args.offset_reset,
    }
    conf_confluent.update(dict(kconfig["kafka"]))
    consumer = Consumer(conf_confluent)

    # Configure SR client
    sr_conf = {
        "url": args.schema_registry,
    }
    sr_conf.update(dict(kconfig["schema-registry"]))
    sr_client = SchemaRegistryClient(sr_conf)
    avro_deserializer = AvroDeserializer(sr_client)

    try:
        consumer.subscribe([args.topic])

        logging.info(
            f"Started consumer {conf_confluent['client.id']} ({conf_confluent['group.id']}) on topic '{args.topic}'"
        )
        while True:
            try:
                msg = consumer.poll(timeout=0.25)
                if msg is not None:
                    if msg.error():
                        raise KafkaException(msg.error())
                    else:
                        avro_event = avro_deserializer(
                            msg.value(),
                            SerializationContext(msg.topic(), MessageField.VALUE),
                        )
                        print(f"Headers: {msg.headers()}")
                        print(
                            f"Key: {None if msg.key() is None else msg.key().decode()}"
                        )
                        print(f"Value: {avro_event}\n")

            except Exception as err:
                logging.error(err)

    except KeyboardInterrupt:
        logging.warning("CTRL-C pressed by user!")
        pass

    finally:
        logging.info(
            f"Closing consumer {conf_confluent['client.id']} ({conf_confluent['group.id']})"
        )
        consumer.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generic Python Avro consumer")
    OFFSET_RESET = [
        "earliest",
        "latest",
    ]
    parser.add_argument(
        "--topic",
        help="Topic name",
        dest="topic",
        type=str,
    )
    parser.add_argument(
        "--config-filename",
        dest="config_filename",
        type=str,
        help=f"Select config filename for additional configuration, such as credentials (files must be inside the folder {FOLDER_CONFIG}/)",
        default=None,
    )
    parser.add_argument(
        "--kafka-section",
        dest="kafka_section",
        type=str,
        help=f"Section in the config file related to the Kafka cluster (e.g. kafka)",
        default=None,
    )
    parser.add_argument(
        "--sr-section",
        dest="sr_section",
        type=str,
        help=f"Section in the config file related to the Schema Registry (e.g. schema-registry)",
        default=None,
    )
    parser.add_argument(
        "--offset-reset",
        dest="offset_reset",
        help=f"Set auto.offset.reset (default: {OFFSET_RESET[0]})",
        type=str,
        default=OFFSET_RESET[0],
        choices=OFFSET_RESET,
    )
    parser.add_argument(
        "--group-id",
        dest="group_id",
        type=str,
        help=f"Consumer's Group ID (default is 'generic-avro-deserialiser')",
        default="generic-avro-deserialiser",
    )
    parser.add_argument(
        "--client-id",
        dest="client_id",
        type=str,
        help=f"Consumer's Client ID (default is 'generic-avro-deserialiser-01')",
        default="generic-avro-deserialiser-01",
    )
    parser.add_argument(
        "--bootstrap-servers",
        dest="bootstrap_servers",
        default="localhost:9092",
        help="Bootstrap broker(s) (host[:port])",
        type=str,
    )
    parser.add_argument(
        "--schema-registry",
        help="Schema Registry (http(s)://host[:port])",
        dest="schema_registry",
        default="http://localhost:8081",
        type=str,
    )

    main(parser.parse_args())
