#!/usr/bin/env python
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

# Python emulator of the Kafka source connector Datagen

import os
import sys
import json
import time
import exrex
import random
import argparse
import avro.schema
import commentjson

from functools import lru_cache
from importlib import import_module
from confluent_kafka import Producer
from confluent_kafka.serialization import (
    SerializationContext,
    MessageField,
)
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer


# Global Variables
FILE_APP = os.path.split(__file__)[-1]
FOLDER_APP = os.path.dirname(__file__)
FOLDER_HEADERS = "headers"
FOLDER_SCHEMAS = "resources"


# General functions
def real_sleep(millisecs: int, start_time: float):
    """Sleep function to take into account the elapsed time in between messages generated/published"""
    total_secs = millisecs / 1000 - (time.time() - start_time)
    if total_secs > 0:
        time.sleep(total_secs)


class AvroParser:
    @staticmethod
    @lru_cache
    def _get_field_type(field_type: str):
        """Internal method (idempotent) to return Python's equivalent type, None if no match"""
        if field_type in ["int", "long"]:
            return int
        elif field_type in ["float", "decimal", "bytes", "double"]:
            return float
        elif field_type == "boolean":
            return bool
        elif field_type == "array":
            return list
        elif field_type == "string":
            return str

    @staticmethod
    @lru_cache
    def _get_static_headers(filename: str) -> dict:
        """Internal method (idempotent) to return static message headers"""
        full_filename = os.path.join(FOLDER_APP, FOLDER_HEADERS, filename)
        if os.path.isfile(full_filename):
            with open(full_filename, "r") as f:
                return commentjson.loads(f.read())
        else:
            sys.exit(
                f"{FILE_APP}: error: Static headers filename not found: {full_filename}"
            )

    @staticmethod
    @lru_cache
    def _get_dynamic_headers_module(filename: str):
        """Internal method (idempotent) to return dynamic message headers' module"""
        full_filename = os.path.join(FOLDER_APP, FOLDER_HEADERS, filename)
        if os.path.isfile(full_filename):
            return import_module(f"{FOLDER_HEADERS}.{filename[:-3]}")
        else:
            sys.exit(
                f"{FILE_APP}: error: Dynamic headers filename not found: {full_filename}"
            )

    @staticmethod
    def data_dict(
        data: dict,
        ctx,
    ) -> dict:
        """
        Returns a dict representation of a data instance for serialization.
        Args:
            data (dict): payload data
            ctx (SerializationContext): Metadata pertaining to the serialization
                operation.
        Returns:
            dict: Dict populated with user attributes to be serialized.
        """
        return dict(data)

    @staticmethod
    def delivery_report(err, msg):
        """
        Reports the failure or success of a message delivery.
        Args:
            err (KafkaError): The error that occurred on None on success.
            msg (Message): The message that was produced or failed.
        Note:
            In the delivery report callback the Message.key() and Message.value()
            will be the binary format as encoded by any configured Serializers and
            not the same object that was passed to produce().
            If you wish to pass the original object(s) for key and value to delivery
            report callback we recommend a bound callback or lambda where you pass
            the objects along.
        """

        if err is not None:
            print(f"> ERROR: Delivery failed for Data record {msg.key()}: {err}\n")
        else:
            print(
                f"> Message successfully produced to {msg.topic()}: Partition = {msg.partition()}, Offset = {msg.offset()}\n"
            )

    @staticmethod
    def _get_type(field_type):
        """Internal method to return field type, pick a random one in case of Union"""
        if isinstance(field_type, list):
            return random.choice(field_type)
        else:
            return field_type

    def __init__(self, avro_schema_filename: str) -> None:
        self.payload_iteration_cache = dict()  # In case of arg.properties INTERATION
        self.keyfield_type = str  # default

        # Read avro schema file (throws exception in case of error)
        if os.path.isfile(avro_schema_filename):
            try:
                with open(avro_schema_filename, "r") as f:
                    self.avro_schema_original = commentjson.loads(f.read())

            except Exception as err:
                sys.exit(
                    f'{FILE_APP}: error: when processing schema file "{avro_schema_filename}": {err}'
                )
        else:
            sys.exit(
                f"{FILE_APP}: error: Schema filename not found: {avro_schema_filename}"
            )

        # Validate avro schema (throws exception in case of error)
        avro.schema.parse(json.dumps(self.avro_schema_original))

        # Cleanup schema
        self.avro_schema = self._cleanup_schema(self.avro_schema_original)

    def _cleanup_schema(self, schema):
        """
        Remove arg.properties from schema (recurring function)
        """
        if isinstance(schema, dict):
            avro_schema = dict()
            for key, value in schema.items():
                if key != "arg.properties":
                    if isinstance(value, list):
                        avro_schema[key] = list()
                        for n in value:
                            avro_schema[key].append(self._cleanup_schema(n))
                    else:
                        avro_schema[key] = self._cleanup_schema(value)
            return avro_schema
        else:
            return schema

    def set_headers(self, headers_filename: str) -> dict:
        """Internal method to return message headers"""
        try:
            if headers_filename.lower().endswith(".py"):
                # Import python module and get dict value from method headers() -> dict:
                return self._get_dynamic_headers_module(headers_filename).headers()
            else:
                return self._get_static_headers(headers_filename)
        except Exception as err:
            sys.exit(
                f'{FILE_APP}: error: when processing headers file "{headers_filename}": {err}'
            )

    def set_key(self, message: dict, key_json: bool, keyfield: str):
        """Set message key"""
        message_key = message[keyfield]
        if key_json:
            message_key = json.dumps({keyfield: message_key})
        else:
            if self.keyfield_type == bool:
                message_key = "true" if message_key else "false"
            elif self.keyfield_type == list:
                message_key = "[" + ",".join(str(item) for item in message_key) + "]"
            else:
                message_key = str(message_key)
        return message_key

    def generate_payload(
        self,
        avro_schema: dict,
        keyfield: str = None,
        is_recurring: bool = False,
    ) -> dict:
        """
        Generate random payload as per AVRO schema
        Args:
            avro_schema (dict): Avro schema with arg.properties
            keyfield (str): Key field name
            is_recurring (bool): Do not set this value, it is used in recurrency cases (array type)
        Returns:
            dict: payload
        """

        # Generated payload
        payload = dict()

        # Check for arg.properties defined on the 1st level of the schema
        #   if so randomly chose options (ONLY OPTIONS IS PARSED FOR NOW)
        args_properties = avro_schema.get("arg.properties")
        if isinstance(args_properties, dict):
            if isinstance(args_properties.get("options"), list):
                payload = random.choice(args_properties.get("options"))

        # Generate payload data/fields types
        payload_fields = dict()
        for field in avro_schema.get("fields", list()):
            if isinstance(field, dict):
                field_name = field.get("name")

                if field_name is not None:
                    field_type = field.get("type")

                    if type(field_type) in [str, list]:
                        payload_fields[field_name] = {
                            "type": self._get_type(field_type),
                            "scale": field.get("scale"),
                            "arg.properties": field.get("arg.properties"),
                        }

                    elif isinstance(field_type, dict):
                        field_type_type = self._get_type(field_type.get("type"))
                        if not is_recurring and keyfield == field_name:
                            self.keyfield_type = self._get_field_type(field_type_type)

                        # arg.properties defined on the field level
                        args_properties = field.get("arg.properties")

                        # arg.properties defined on the field type level
                        if args_properties is None:
                            args_properties = field_type.get("arg.properties")

                        if args_properties is None:
                            args_properties = dict()

                        if field_type_type == "array":
                            field_items = field_type.get("items")
                            if isinstance(field_items, dict):
                                min_items = args_properties.get("length", dict()).get(
                                    "min",
                                    1,
                                )
                                max_items = args_properties.get("length", dict()).get(
                                    "max",
                                    1,
                                )
                                payload[field_name] = list()
                                for _ in range(random.randint(min_items, max_items)):
                                    payload[field_name].append(
                                        self.generate_payload(
                                            {
                                                "fields": field_items.get(
                                                    "fields", list()
                                                ),
                                                "arg.properties": field_items.get(
                                                    "arg.properties"
                                                ),
                                            },
                                            is_recurring=True,
                                        )
                                    )

                        elif field_type_type == "record":
                            payload[field_name] = self.generate_payload(
                                {
                                    "fields": field_type.get("fields", list()),
                                    "arg.properties": field_type.get("arg.properties"),
                                },
                                is_recurring=True,
                            )

                        else:
                            if isinstance(field_type_type, str):
                                payload_fields[field_name] = {
                                    "type": field_type_type,
                                    "arg.properties": args_properties,
                                    "scale": field_type.get("scale"),
                                }

        # Generate random data
        for field_name, params in payload_fields.items():

            if payload.get(field_name) is None:
                payload[field_name] = None

                # No arg.properties defined, set one
                if not (
                    isinstance(params.get("arg.properties"), dict)
                    and len(params.get("arg.properties"))
                ):
                    missing_field_type = self._get_field_type(
                        payload_fields[field_name].get("type")
                    )
                    if missing_field_type == int:
                        params["arg.properties"] = {
                            "range": {
                                "min": 1,
                                "max": 9999,
                            }
                        }
                    elif missing_field_type == float:
                        params["scale"] = 2
                        params["arg.properties"] = {
                            "range": {
                                "min": 0,
                                "max": 99.99,
                            }
                        }
                    elif missing_field_type == str:
                        params["arg.properties"] = {
                            "regex": "[a-zA-Z1-9]{4,8}",
                        }
                    elif missing_field_type == bool:
                        params["arg.properties"] = {
                            "options": [
                                True,
                                False,
                            ]
                        }
                    else:  # set none, in case of array
                        params["arg.properties"] = {None: None}

                args_properties_type = next(iter(params.get("arg.properties")))

                # OPTIONS
                if args_properties_type == "options":
                    if isinstance(params["arg.properties"][args_properties_type], list):
                        payload[field_name] = random.choice(
                            params["arg.properties"][args_properties_type]
                        )

                # INTERATION
                elif args_properties_type == "iteration":
                    if isinstance(params["arg.properties"][args_properties_type], dict):
                        iteration_start = params["arg.properties"][
                            args_properties_type
                        ].get("start", 0)
                        iteration_step = params["arg.properties"][
                            args_properties_type
                        ].get("step", 1)
                        if self.payload_iteration_cache.get(field_name) is None:
                            self.payload_iteration_cache[field_name] = iteration_start
                        else:
                            self.payload_iteration_cache[field_name] += iteration_step
                        payload[field_name] = self.payload_iteration_cache[field_name]

                # RANGE
                elif args_properties_type == "range":
                    if isinstance(params["arg.properties"][args_properties_type], dict):
                        range_min = params["arg.properties"][args_properties_type].get(
                            "min", 0
                        )
                        range_max = params["arg.properties"][args_properties_type].get(
                            "max", 1
                        )
                        if isinstance(range_min, int) and isinstance(range_max, int):
                            payload[field_name] = random.randrange(range_min, range_max)
                        else:
                            value = random.uniform(range_min, range_max)
                            if isinstance(params.get("scale"), int):
                                value = round(value, params.get("scale"))
                            payload[field_name] = value

                # REGEX
                elif args_properties_type == "regex":
                    if isinstance(params["arg.properties"][args_properties_type], str):
                        payload[field_name] = exrex.getone(
                            params["arg.properties"][args_properties_type]
                        )

        return payload


def main(args):
    avro_schema_filename = os.path.join(
        FOLDER_APP,
        FOLDER_SCHEMAS,
        args.schema_filename,
    )
    avsc = AvroParser(avro_schema_filename)

    if args.dry_run:
        print(f"Producing {args.iterations} messages in dry-run mode. ^C to exit.\n")
        try:
            for msg in range(args.iterations):
                start_time = time.time()
                message = avsc.generate_payload(
                    avsc.avro_schema_original,
                    keyfield=args.keyfield,
                )
                print(f"message #{msg+1}: {message}")

                # Set headers
                if args.headers_filename:
                    message_headers = avsc.set_headers(args.headers_filename)
                    print(f"headers: {message_headers}")

                # Set key
                if message.get(args.keyfield):
                    message_key = avsc.set_key(message, args.key_json, args.keyfield)
                    print(f"key: {message_key}")

                print()
                real_sleep(args.interval, start_time)

        except KeyboardInterrupt:
            print("CTRL-C pressed by user")

    else:
        producer = None
        try:
            schema_registry_conf = {
                "url": args.schema_registry,
            }
            schema_registry_client = SchemaRegistryClient(schema_registry_conf)

            producer_conf = {
                "acks": 0,
                "bootstrap.servers": args.bootstrap_servers,
            }
            producer = Producer(producer_conf)

            avro_serializer = AvroSerializer(
                schema_registry_client,
                json.dumps(avsc.avro_schema),
                avsc.data_dict,
            )

            print(
                f"Producing {args.iterations} messages to topic '{args.topic}'. ^C to exit.\n"
            )
            for msg in range(args.iterations):
                # Serve on_delivery callbacks from previous calls to produce()
                producer.poll(0.0)
                start_time = time.time()
                try:
                    message = avsc.generate_payload(
                        avsc.avro_schema_original,
                        keyfield=args.keyfield,
                    )

                    producer_args = {
                        "topic": args.topic,
                        "value": avro_serializer(
                            message,
                            SerializationContext(
                                args.topic,
                                MessageField.VALUE,
                            ),
                        ),
                    }

                    if not args.silent:
                        producer_args.update({"on_delivery": avsc.delivery_report})
                        print(f"message #{msg+1}: {message}")

                    # Set headers
                    if args.headers_filename:
                        message_headers = avsc.set_headers(args.headers_filename)
                        producer_args.update({"headers": message_headers})
                        if not args.silent:
                            print(f"headers: {message_headers}")

                    # Set key
                    if message.get(args.keyfield):
                        message_key = avsc.set_key(
                            message, args.key_json, args.keyfield
                        )
                        producer_args.update({"key": message_key})
                        if not args.silent:
                            print(f"key: {message_key}")

                    # Publish message
                    producer.produce(**producer_args)

                except KeyboardInterrupt:
                    print("CTRL-C pressed by user")
                    break

                except ValueError as err:
                    print("> ERROR: Invalid input, discarding record: {err}")
                    continue

                finally:
                    real_sleep(args.interval, start_time)

            print("\nFlushing messages...")
            producer.flush()

        except Exception as err:
            sys.exit(f"{FILE_APP}: error: when publishing messages: {err}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Python emulator of the Kafka source connector Datagen"
    )
    parser.add_argument(
        "--schema-filename",
        help=f"Avro schema file name, files must be inside the folder {FOLDER_SCHEMAS}/",
        dest="schema_filename",
        required=True,
        type=str,
    )
    parser.add_argument(
        "--keyfield",
        help="Name of the field to be used as message key (required if argument --key-json is set)",
        dest="keyfield",
        type=str,
        default=None,
        required="--key-json" in sys.argv,
    )
    parser.add_argument(
        "--key-json",
        dest="key_json",
        action="store_true",
        help="Set key as JSON -> {{keyfield: keyfield_value}}",
    )
    parser.add_argument(
        "--topic",
        help="Topic name (required if argument --dry-run is not set)",
        dest="topic",
        required="--dry-run" not in sys.argv,
        type=str,
    )
    parser.add_argument(
        "--headers-filename",
        dest="headers_filename",
        type=str,
        help=f"Select headers filename, files must be inside the folder {FOLDER_HEADERS}/ (if not set, no headers will be set on the message)",
        default=None,
    )
    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Generate and display messages without having them publish",
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
        help="Schema Registry (http(s)://host[:port]",
        dest="schema_registry",
        default="http://localhost:8081",
        type=str,
    )
    parser.add_argument(
        "--iterations",
        help="Number of messages to be sent",
        dest="iterations",
        default=9999999999999,
        type=int,
    )
    parser.add_argument(
        "--interval",
        help="Max interval between messages (in milliseconds)",
        dest="interval",
        default=500,
        type=int,
    )
    parser.add_argument(
        "--silent",
        dest="silent",
        action="store_true",
        help="Do not display results on screen (not applicable in dry-run mode)",
    )

    main(parser.parse_args())
