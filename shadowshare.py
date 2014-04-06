#!/usr/bin/env python3.4

from client import client
import argparse

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='command')

parser_put_for = subparsers.add_parser('put-for')
parser_put_for.add_argument('user_name')
parser_put_for.add_argument('file_name')

parser_get_from = subparsers.add_parser('get-from')
parser_get_from.add_argument('user_name')

parser_register = subparsers.add_parser('register')
parser_register.add_argument('user_name')

parser_get = subparsers.add_parser('get')
parser_put = subparsers.add_parser('put')
parser_put.add_argument('file_name')

args = parser.parse_args()

if args.command == "put-for":
    client.put_for(args.user_name, args.file_name)
elif args.command == "get-from":
    client.get_from(args.user_name)
elif args.command == "register":
    client.register(args.user_name)
elif args.command == "get":
    client.get()
elif args.command == "put":
    client.put(args.file_name)
