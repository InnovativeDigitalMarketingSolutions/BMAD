#!/usr/bin/env python3
"""
Product Owner Agent voor BMAD
"""
import argparse


def main():
    parser = argparse.ArgumentParser(description="Product Owner Agent")
    parser.add_argument(
        "command", nargs="?", default="help", help="Commando voor de agent"
    )
    args = parser.parse_args()
    if args.command == "help":
        print("Beschikbare commando's: help, create-story, show-vision, ...")
    else:
        print(f"Commando '{args.command}' wordt uitgevoerd (stub)")


if __name__ == "__main__":
    main()
