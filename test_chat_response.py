"""Quick test script to query /api/v1/ai/chat and display structured response.

Usage (Windows PowerShell):
  python test_chat_response.py --message "Describe the safety procedure" --url http://localhost:8000
Optionally add --conversation-id conv_test1

No authentication header is sent (endpoint supports anonymous access).
"""
import argparse
import json
import sys
import textwrap
from datetime import datetime, timezone
from typing import Optional

import requests

DEFAULT_URL = "http://localhost:8000"
CHAT_ENDPOINT = "/api/v1/ai/chat"


def call_chat(base_url: str, message: str, conversation_id: Optional[str]=None, concise: bool=False) -> dict:
    payload = {"message": message}
    if conversation_id:
        payload["conversation_id"] = conversation_id
    if concise:
        payload["concise"] = True
    url = base_url.rstrip("/") + CHAT_ENDPOINT
    resp = requests.post(url, json=payload, timeout=120)
    try:
        data = resp.json()
    except ValueError:
        print("Non-JSON response status=", resp.status_code, file=sys.stderr)
        print(resp.text[:1000], file=sys.stderr)
        raise SystemExit(1)
    if resp.status_code != 200:
        print("Error status:", resp.status_code, file=sys.stderr)
        print(json.dumps(data, indent=2)[:2000], file=sys.stderr)
        raise SystemExit(1)
    return data


def extract_sections(response_text: str) -> dict:
    """Basic parsing of required sections to quickly validate formatting."""
    sections = {}
    current = None
    for line in response_text.splitlines():
        if line.startswith("## "):
            current = line.strip().lstrip('# ').strip()
            sections[current] = []
        elif current:
            sections[current].append(line)
    # Convert lists to joined strings
    return {k: "\n".join(v).strip() for k, v in sections.items()}


def validate_structure(sections: dict) -> list:
    required = [
        "Problem Analysis",
        "Troubleshooting Steps",
        "Additional Recommendations",
        "Next Steps"
    ]
    missing = [sec for sec in required if sec not in sections]
    return missing


def main():
    parser = argparse.ArgumentParser(description="Test AI chat structured response")
    parser.add_argument("--url", default=DEFAULT_URL, help="Base API URL (default: %(default)s)")
    # Make message optional; if omitted we'll prompt interactively
    parser.add_argument("message", nargs="?", help="Question to ask the AI (positional). If omitted you'll be prompted.")
    parser.add_argument("--message", dest="message_flag", help="Alternate way to supply the question (overrides positional).")
    parser.add_argument("--conversation-id", help="Conversation ID to reuse context")
    parser.add_argument("--concise", action="store_true", help="Request steps-only concise output")
    parser.add_argument("--save", metavar="FILE", help="Save full raw response to a file")
    parser.add_argument("--no-truncate", action="store_true", help="Do not truncate printed raw response to 2000 chars")
    args = parser.parse_args()

    # Resolve message precedence: --message flag > positional > prompt
    message = args.message_flag or args.message
    if not message:
        try:
            message = input("Enter your troubleshooting question: ").strip()
        except KeyboardInterrupt:
            print("\nAborted.")
            return
    if not message:
        print("No message provided.")
        return

    start = datetime.now(timezone.utc)
    data = call_chat(args.url, message, args.conversation_id, concise=args.concise)
    elapsed = (datetime.now(timezone.utc) - start).total_seconds()

    response_text = data.get("response", "")
    if args.save:
        try:
            with open(args.save, 'w', encoding='utf-8') as f:
                f.write(response_text)
            print(f"Saved full response to {args.save}")
        except Exception as e:
            print(f"Failed to save response: {e}")

    display_text = response_text if args.no_truncate else response_text[:2000]
    label = "full" if args.no_truncate else "first 2000 chars"
    mode = "CONCISE" if args.concise else "FULL"
    print(f"=== Raw Response [{mode}] ({label}) ===")
    print(display_text)
    print()

    sections = extract_sections(response_text)
    missing = validate_structure(sections)

    print("=== Section Summary ===")
    for name, content in sections.items():
        snippet = textwrap.shorten(content.replace('\n', ' '), width=140, placeholder='...')
        print(f"- {name}: {len(content)} chars | {snippet}")
    if missing:
        print("\nMissing required sections:", ", ".join(missing))
    else:
        print("\nAll required sections present.")

    # Quick step heading count
    step_count = sum(1 for line in response_text.splitlines() if line.strip().startswith('### Step '))
    # Extract sources if present
    sources = None
    if '\n---\n**Sources:**' in response_text:
        sources = response_text.split('\n---\n**Sources:**', 1)[1].strip()
    if sources:
        print("\nSources:")
        print(sources)
    print(f"\nDetected {step_count} troubleshooting steps.")

    print(f"\nAPI latency: {elapsed:.2f}s")


if __name__ == "__main__":
    main()
